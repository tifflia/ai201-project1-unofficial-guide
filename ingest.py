"""Document ingestion for The Unofficial Guide (Milestone 3).

`collect_documents()` scrapes the 10 sources listed in planning.md and writes one
cleaned plain-text file per source into ./documents. Each file starts with a small
metadata header (source, title, url, description) so attribution stays attached to
the text through the rest of the pipeline, then a `---` divider, then the body.

Two ingestion paths, chosen per source:
  * STATIC  -> requests + BeautifulSoup   (The Amherst Student: server-rendered HTML)
  * JS      -> Playwright (Chromium)      (Reddit, amherst.edu, College Confidential:
                                           content rendered client-side / behind a JS
                                           challenge, so a plain GET returns no text)

After collection, `chunk_documents()` reads those .txt files back, separates the
metadata header from the body, and splits each body into overlapping chunks ready
for embedding (Milestone 4). Every chunk carries its source metadata + a unique
chunk_id so a retrieved claim can always be traced back to its source.

Run:  python ingest.py collect   # scrape the 10 sources -> documents/*.txt
      python ingest.py chunk     # chunk those files, write chunks_preview.txt
      python ingest.py all       # both
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from config import DOCS_PATH

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# --- The 10 sources from planning.md -----------------------------------------
# kind drives which extractor runs; method records how we fetch the page.
SOURCES = [
    {
        "id": 1,
        "name": "The Amherst Student",
        "description": "An article reviewing laundry rooms on campus.",
        "url": "https://amherststudent.com/article/cleaning-up-we-take-a-quick-spin-through-the-four/",
        "method": "static",
        "kind": "ghost",
        "slug": "laundry-room-review",
    },
    {
        "id": 2,
        "name": "The Amherst Student",
        "description": "Shane Dillon '26 expresses gratitude for his time living in Lipton House.",
        "url": "https://amherststudent.com/article/thank-you-lipton/",
        "method": "static",
        "kind": "ghost",
        "slug": "thank-you-lipton",
    },
    {
        "id": 3,
        "name": "r/amherstcollege",
        "description": "A Reddit thread where people mention unexpected cons of student housing.",
        "url": "https://www.reddit.com/r/amherstcollege/comments/1ldaqtb/dorm_honest_review/",
        "method": "js",
        "kind": "reddit",
        "slug": "reddit-dorm-honest-review",
    },
    {
        "id": 4,
        "name": "r/amherstcollege",
        "description": "A Reddit thread comparing and ranking dorms.",
        "url": "https://www.reddit.com/r/amherstcollege/comments/1shgint/best_and_worst_dorms/",
        "method": "js",
        "kind": "reddit",
        "slug": "reddit-best-and-worst-dorms",
    },
    {
        "id": 5,
        "name": "The Amherst Student",
        "description": "Brenda Tenorio '27 reflects on the experience of living in Cohan Hall.",
        "url": "https://amherststudent.com/article/satire-why-cohan-needs-its-one-room-doubles/",
        "method": "static",
        "kind": "ghost",
        "slug": "cohan-one-room-doubles",
    },
    {
        "id": 6,
        "name": "amherst.edu",
        "description": "A page listing all current theme and language communities on campus.",
        "url": "https://www.amherst.edu/campuslife/housing-dining/residential-life/theme",
        "method": "js",
        "kind": "amherst_edu",
        "slug": "theme-communities",
    },
    {
        "id": 7,
        "name": "amherst.edu",
        "description": "A page listing residential area groups and the housing accommodations in some of them.",
        "url": "https://www.amherst.edu/campuslife/housing-dining/residential-life/residential-areas",
        "method": "js",
        "kind": "amherst_edu",
        "slug": "residential-areas",
    },
    {
        "id": 8,
        "name": "The Amherst Student",
        "description": "An article describing the old room draw process, revealing desirable dorms.",
        "url": "https://amherststudent.amherst.edu/article/2016/04/13/room-draw-chaos.html",
        "method": "static",
        "kind": "drupal",
        "slug": "room-draw-chaos",
    },
    {
        "id": 9,
        "name": "The Amherst Student",
        "description": 'Campus social life and gatherings after the destruction of "the socials".',
        "url": "https://amherststudent.amherst.edu/article/2017/04/11/scattering-campus-social-life.html",
        "method": "static",
        "kind": "drupal",
        "slug": "scattering-campus-social-life",
    },
    {
        "id": 10,
        "name": "College Confidential",
        "description": 'A forum thread discussing the best freshman dorms and living on "the hill".',
        "url": "https://talk.collegeconfidential.com/t/dorms/473186",
        "method": "js",
        "kind": "discourse",
        "slug": "collegeconfidential-best-freshman-dorms",
    },
]


# --- Text cleaning ------------------------------------------------------------
def clean_text(text: str) -> str:
    """Normalize whitespace and drop empty/boilerplate-only lines."""
    if not text:
        return ""
    # Normalize unicode spaces and strip per-line trailing whitespace.
    text = text.replace("\xa0", " ").replace("​", "")
    # Standalone junk lines (image alt-text placeholders, bare nav labels).
    NOISE_LINES = {"image", "learn more"}
    lines = [ln.rstrip() for ln in text.splitlines()]
    cleaned = []
    for ln in lines:
        s = ln.strip()
        if not s:
            cleaned.append("")
            continue
        if s.lower() in NOISE_LINES:
            continue
        cleaned.append(ln)
    # Drop immediately-repeated identical lines (e.g. a heading that also appears as an image caption right beneath it).
    deduped = []
    for ln in cleaned:
        if ln.strip() and deduped and deduped[-1].strip() == ln.strip():
            continue
        deduped.append(ln)
    text = "\n".join(deduped)
    # Collapse 3+ blank lines into a single blank line.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# --- Static extractors (requests + BeautifulSoup) -----------------------------
def fetch_static(url: str) -> str:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp.text


def _soup_text(node) -> str:
    """Text of a BeautifulSoup node with paragraph/break structure preserved."""
    for tag in node.find_all(["script", "style", "noscript"]):
        tag.decompose()
    return node.get_text("\n", strip=True)


def extract_ghost(html: str) -> tuple[str, str]:
    """The Amherst Student (amherststudent.com — Ghost CMS)."""
    soup = BeautifulSoup(html, "lxml")
    title_el = soup.select_one(".gh-article-title") or soup.find("h1")
    title = title_el.get_text(strip=True) if title_el else ""
    body_el = soup.select_one(".gh-content") or soup.find("article")
    body = _soup_text(body_el) if body_el else ""
    return title, body


def extract_drupal(html: str) -> tuple[str, str]:
    """The Amherst Student archive (amherststudent.amherst.edu — Drupal).

    Captures the article body and, if present, reader comments — student voices
    in the comments are useful for the housing domain, so we keep them under a
    labelled section.
    """
    soup = BeautifulSoup(html, "lxml")
    # Real headline lives in <title> ("Headline | The Amherst Student"); the on-page #page-title is just the section name ("Opinion").
    title = ""
    if soup.title:
        title = soup.title.get_text(strip=True).split("|")[0].strip()

    body_el = soup.select_one(".field-name-body")
    body = _soup_text(body_el) if body_el else ""

    comments = []
    for c in soup.select(".comment-content, .field-name-comment-body"):
        t = _soup_text(c)
        if t:
            comments.append(t)
    if comments:
        body += "\n\n=== Reader comments ===\n\n" + "\n\n---\n\n".join(comments)
    return title, body


# --- JS extractors (Playwright) -----------------------------------------------
def extract_amherst_edu(page) -> tuple[str, str]:
    """amherst.edu residential-life pages (client-side rendered)."""
    page.goto(page_url_marker.url, wait_until="networkidle", timeout=60000)
    title = page.title().split("|")[0].strip()
    main = page.query_selector("main") or page.query_selector("[role=main]")
    text = main.inner_text() if main else page.inner_text("body")
    return title, text


def extract_reddit(page) -> tuple[str, str]:
    """Reddit thread: original post + comment tree (shreddit web components)."""
    page.goto(page_url_marker.url, wait_until="domcontentloaded", timeout=60000)
    # Wait out the JS challenge / hydration, then nudge lazy comment loading.
    page.wait_for_timeout(4000)
    try:
        page.wait_for_selector("shreddit-comment", timeout=15000)
    except Exception:
        pass
    for _ in range(6):
        page.mouse.wheel(0, 20000)
        page.wait_for_timeout(1200)

    data = page.evaluate(
        """
        () => {
          const post = document.querySelector('shreddit-post');
          const title = post ? (post.getAttribute('post-title') || '') : (document.title || '');
          let body = '';
          if (post) {
            const tb = post.querySelector('[slot="text-body"]');
            if (tb) body = tb.innerText.trim();
          }
          const comments = [];
          document.querySelectorAll('shreddit-comment').forEach(c => {
            const author = c.getAttribute('author') || '[deleted]';
            const depth = parseInt(c.getAttribute('depth') || '0', 10);
            const own = c.querySelector(':scope > [slot="comment"]');
            const text = own ? own.innerText.trim() : '';
            if (text) comments.push({author, depth, text});
          });
          return {title, body, comments};
        }
        """
    )

    parts = []
    if data.get("body"):
        parts.append(data["body"])
    if data.get("comments"):
        parts.append("=== Comments ===")
        for c in data["comments"]:
            indent = "    " * min(c["depth"], 6)
            author = c["author"].strip("[]") or "deleted"
            block = "\n".join(indent + ln for ln in c["text"].splitlines())
            parts.append(f"{indent}[{author}]\n{block}")
    return data.get("title", ""), "\n\n".join(parts)


def extract_discourse(page) -> tuple[str, str]:
    """College Confidential (Discourse forum).

    Discourse virtualises its post stream — only the handful of on-screen posts
    are in the DOM at any time — so we accumulate posts *while* scrolling, keyed
    by post id, instead of reading them all at the end. This site also stores the
    post body as escaped HTML *text* inside `.cooked`, so we un-escape it (via a
    throwaway element) to recover the real prose rather than literal `<p>` tags.
    """
    page.goto(page_url_marker.url, wait_until="domcontentloaded", timeout=60000)
    try:
        page.wait_for_selector(".topic-post", timeout=20000)
    except Exception:
        pass
    title = page.title().split(" - ")[0].strip()

    collect_js = """
        () => {
          const posts = [];
          document.querySelectorAll('.topic-post').forEach(p => {
            const cooked = p.querySelector('.cooked');
            if (!cooked) return;
            const art = p.querySelector('article[data-post-id]') || p;
            const id = art.getAttribute('data-post-id')
                       || p.id || cooked.innerText.slice(0, 40);
            const userEl = p.querySelector(
              '.username a, .first.username, [itemprop="author"] [itemprop="name"], .names .username');
            const author = userEl ? userEl.innerText.trim() : 'user';
            // .cooked holds escaped HTML as text on this site — un-escape it.
            const tmp = document.createElement('div');
            tmp.innerHTML = cooked.innerText;
            const text = (tmp.innerText || cooked.innerText).trim();
            if (text) posts.push({id, author, text});
          });
          return posts;
        }
    """

    seen, ordered = set(), []
    stable = 0
    for _ in range(60):
        for post in page.evaluate(collect_js):
            if post["id"] not in seen:
                seen.add(post["id"])
                ordered.append(post)
        before = len(seen)
        page.mouse.wheel(0, 4000)
        page.wait_for_timeout(700)
        stable = stable + 1 if len(seen) == before else 0
        if stable >= 8:  # no new posts across several scrolls -> reached the end
            break

    parts = [f"[{p['author']}]\n{p['text']}" for p in ordered]
    return title, "\n\n---\n\n".join(parts)


# Lightweight holder so the Playwright extractors can read the current URL without changing their (page) signature.
class _UrlMarker:
    url = ""


page_url_marker = _UrlMarker()


# --- File writing -------------------------------------------------------------
def write_document(src: dict, title: str, body: str) -> Path:
    docs_dir = Path(DOCS_PATH)
    docs_dir.mkdir(parents=True, exist_ok=True)
    body = clean_text(body)
    header = (
        f"source: {src['name']}\n"
        f"title: {title}\n"
        f"url: {src['url']}\n"
        f"description: {src['description']}\n"
        f"method: {src['method']}\n"
        f"---\n\n"
    )
    out_path = docs_dir / f"{src['id']:02d}_{src['slug']}.txt"
    out_path.write_text(header + body + "\n", encoding="utf-8")
    return out_path


# --- Orchestration ------------------------------------------------------------
def collect_documents() -> None:
    """Scrape all 10 sources and write cleaned .txt files into ./documents."""
    static_sources = [s for s in SOURCES if s["method"] == "static"]
    js_sources = [s for s in SOURCES if s["method"] == "js"]

    results = []

    # ---- Static path (requests + BeautifulSoup) ----
    static_extractors = {"ghost": extract_ghost, "drupal": extract_drupal}
    for src in static_sources:
        try:
            html = fetch_static(src["url"])
            title, body = static_extractors[src["kind"]](html)
            path = write_document(src, title, body)
            results.append((src, len(body), path, None))
            print(f"[{src['id']:02d}] static  ok  {len(body):>6} chars  -> {path.name}")
        except Exception as e:  # noqa: BLE001 - report and continue
            results.append((src, 0, None, str(e)))
            print(f"[{src['id']:02d}] static  FAIL  {src['url']}\n       {e}")
        time.sleep(1)

    # ---- JS path (Playwright) ----
    if js_sources:
        from playwright.sync_api import sync_playwright

        js_extractors = {
            "reddit": extract_reddit,
            "amherst_edu": extract_amherst_edu,
            "discourse": extract_discourse,
        }
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1280, "height": 1800},
            )
            page = context.new_page()
            for src in js_sources:
                try:
                    page_url_marker.url = src["url"]
                    title, body = js_extractors[src["kind"]](page)
                    path = write_document(src, title, body)
                    results.append((src, len(body), path, None))
                    print(f"[{src['id']:02d}] js      ok  {len(clean_text(body)):>6} chars  -> {path.name}")
                except Exception as e:  # noqa: BLE001
                    results.append((src, 0, None, str(e)))
                    print(f"[{src['id']:02d}] js      FAIL  {src['url']}\n       {e}")
            browser.close()

    failures = [r for r in results if r[3]]
    print(f"\nCollected {len(results) - len(failures)}/{len(SOURCES)} sources "
          f"into {DOCS_PATH}/")
    if failures:
        print("Failures:")
        for src, _, _, err in failures:
            print(f"  [{src['id']:02d}] {src['url']} :: {err}")
        sys.exit(1)


# --- Chunking (Milestone 3) ---------------------------------------------------
CHUNK_SIZE = 900
OVERLAP = 150
MIN_LENGTH = 100  # drop trailing fragments too short to carry meaning

HEADER_KEYS = ("source", "title", "url", "description", "method")


def parse_document(raw: str) -> tuple[dict, str]:
    """Split a collected .txt file into its metadata header and body text.

    Files written by collect_documents() start with `key: value` lines, then a
    `---` divider, then the body. Returns (metadata_dict, body)."""
    header_part, sep, body = raw.partition("\n---\n")
    if not sep:  # no header divider found -> treat the whole file as body
        return {}, raw.strip()
    meta = {}
    for line in header_part.splitlines():
        key, colon, value = line.partition(":")
        if colon and key.strip() in HEADER_KEYS:
            meta[key.strip()] = value.strip()
    return meta, body.strip()


def load_documents() -> list[dict]:
    """Load every .txt file from DOCS_PATH, parsing header + body for each."""
    documents = []
    for path in sorted(Path(DOCS_PATH).glob("*.txt")):
        meta, body = parse_document(path.read_text(encoding="utf-8"))
        documents.append({
            "filename": path.name,
            "stem": path.stem,      # e.g. "03_reddit-dorm-honest-review"
            "meta": meta,
            "text": body,
        })
    print(f"Loaded {len(documents)} document(s): {[d['stem'] for d in documents]}")
    return documents


def chunk_document(doc: dict) -> list[dict]:
    """Split one loaded document into overlapping chunks ready for embedding.

    Character-based sliding window (CHUNK_SIZE, stepping CHUNK_SIZE - OVERLAP so
    each chunk shares OVERLAP characters with the tail of the previous one).
    Every chunk carries the document's source metadata plus a unique chunk_id,
    so retrieval can attribute each chunk back to its origin."""
    text = doc["text"]
    meta = doc["meta"]
    prefix = doc["stem"]
    chunks = []
    counter = 0

    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk_text = text[start:end].strip()
        if len(chunk_text) >= MIN_LENGTH:
            chunks.append({
                "text": chunk_text,
                "chunk_id": f"{prefix}_{counter}",
                "source": meta.get("source", ""),
                "title": meta.get("title", ""),
                "url": meta.get("url", ""),
            })
            counter += 1
        start += CHUNK_SIZE - OVERLAP

    return chunks


def chunk_documents(write_preview: bool = False) -> list[dict]:
    """Load all collected documents and chunk them into one flat list."""
    documents = load_documents()
    all_chunks = []
    for doc in documents:
        doc_chunks = chunk_document(doc)
        all_chunks.extend(doc_chunks)
        print(f"  {doc['stem']:<45} {len(doc['text']):>6} chars -> {len(doc_chunks)} chunk(s)")

    print(f"\nProduced {len(all_chunks)} chunk(s) from {len(documents)} document(s).")

    if write_preview:
        preview_path = Path(DOCS_PATH).parent / "chunks_preview.txt"
        with preview_path.open("w", encoding="utf-8") as f:
            for c in all_chunks:
                f.write(f"===== {c['chunk_id']} | {c['source']} | {c['title']} =====\n")
                f.write(f"url: {c['url']}\n")
                f.write(f"({len(c['text'])} chars)\n\n")
                f.write(c["text"] + "\n\n")
        print(f"Wrote chunk preview -> {preview_path}")

    return all_chunks


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "collect"
    if mode == "collect":
        collect_documents()
    elif mode == "chunk":
        chunk_documents(write_preview=True)
    elif mode == "all":
        collect_documents()
        chunk_documents(write_preview=True)
    else:
        print(f"Unknown mode {mode!r}. Use: collect | chunk | all")
        sys.exit(1)
