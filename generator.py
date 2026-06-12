import re

from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)


SYSTEM_PROMPT = (
    "You are The Unofficial Guide, an assistant that answers questions about "
    "on-campus housing at Amherst College using real student testimonies and "
    "articles.\n\n"
    "Follow these rules strictly:\n"
    "1. Answer USING ONLY the numbered sources provided in the context below. "
    "Do not use any outside knowledge about Amherst, its dorms, or campus life. "
    "If the sources disagree, present the different perspectives rather than "
    "picking one.\n"
    "2. Ground every claim. After each claim, cite the source(s) it came from "
    "using ONLY the bracketed source numbers shown in the context, e.g. [1] or "
    "[2][3]. Never cite names, usernames, or anything other than those numbers. "
    "If several numbered sources say the same thing, cite each relevant number.\n"
    "3. If the provided sources do not contain enough information to answer the "
    "question, say so plainly (\"The sources I have don't cover that\") instead "
    "of guessing. Do NOT mention a dorm unless it appears in the sources.\n"
    "4. Keep the tone helpful and conversational, like an upperclassman giving "
    "honest advice — but every specific fact must trace back to a source."
)


def _format_context(retrieved_chunks):
    """Turn retrieved chunks into a numbered context block for the prompt.

    Numbering is per unique *document*, not per chunk: several retrieved chunks
    often come from the same source (e.g. one forum thread split into many
    chunks), so every chunk from a given document shares one [n]."""
    numbers = _document_numbers(retrieved_chunks)
    blocks = []
    for chunk in retrieved_chunks:
        n = numbers[_document_key(chunk)]
        label = chunk.get("title") or chunk.get("source") or "Source"
        source = chunk.get("source", "")
        header = f"[{n}] {label}"
        if source and source != label:
            header += f" ({source})"
        blocks.append(f"{header}\n{chunk['text']}")
    return "\n\n---\n\n".join(blocks)


def _document_key(chunk):
    """A stable identity for the document a chunk came from. Prefer url, then
    title, then source — whichever is the most specific value present."""
    return chunk.get("url") or chunk.get("title") or chunk.get("source") or ""


def _document_numbers(retrieved_chunks):
    """Map each unique document key to a citation number, assigned in the order
    documents first appear in the retrieved chunks."""
    numbers = {}
    for chunk in retrieved_chunks:
        key = _document_key(chunk)
        if key not in numbers:
            numbers[key] = len(numbers) + 1
    return numbers


def _cited_numbers(answer):
    """Return the set of source numbers the model actually cited as [n] in its
    answer, so the Sources list can be limited to what was really used."""
    return {int(n) for n in re.findall(r"\[(\d+)\]", answer)}


def _format_sources(retrieved_chunks, cited):
    """Build a deduplicated 'Sources' list keyed by the same [n] numbers used in
    the context — one line per unique document. Only documents the answer
    actually cited (numbers in `cited`) are listed, so a retrieved-but-unused
    source doesn't show up."""
    numbers = _document_numbers(retrieved_chunks)
    seen = set()
    lines = []
    for chunk in retrieved_chunks:
        key = _document_key(chunk)
        n = numbers[key]
        if key in seen or n not in cited:
            continue
        seen.add(key)
        label = chunk.get("title") or chunk.get("source") or "Source"
        url = chunk.get("url", "")
        line = f"[{n}] {label}"
        if url:
            line += f" — {url}"
        lines.append(line)
    return "\n".join(lines)


def debug_report(query, retrieved_chunks, answer):
    """Console-only view of the FULL retrieval for debugging (never shown to the
    user). Lists every retrieved chunk with its document number, distance, and a
    text preview, and marks whether the answer actually cited that document —
    so you can see retrieved-but-unused sources and weak-distance matches that
    the cited-only Sources list hides."""
    numbers = _document_numbers(retrieved_chunks)
    cited = _cited_numbers(answer)
    lines = [f"[debug] retrieval for {query!r} — {len(retrieved_chunks)} chunk(s)"]
    if not retrieved_chunks:
        lines.append("  (nothing passed the distance filter in retrieve())")
        return "\n".join(lines)
    for chunk in retrieved_chunks:
        n = numbers[_document_key(chunk)]
        mark = "CITED " if n in cited else "unused"
        preview = chunk["text"].replace("\n", " ")[:70]
        lines.append(
            f"  [{n}] {mark} dist={chunk.get('distance', 0):.3f} "
            f"{chunk.get('source', '')} | {preview}"
        )
    unused = sorted(set(numbers.values()) - cited)
    if unused:
        lines.append(f"  retrieved but NOT cited: {unused}")
    return "\n".join(lines)


def generate_response(query, retrieved_chunks):
    """Generate a grounded, cited answer from retrieved housing chunks.

    `retrieved_chunks` is the list returned by retrieve(). Each item is a dict
    with "text", "source", "title", "url", and "distance". Returns a plain
    string: the model's answer followed by a numbered Sources list.
    """
    if not retrieved_chunks:
        return (
            "I couldn't find anything relevant in the guide's sources for that "
            "question. Try rephrasing, or ask about a specific dorm, residential "
            "area, or part of campus life."
        )

    context = _format_context(retrieved_chunks)

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Context (student testimonies and articles):\n\n{context}\n\n"
                    f"Question: {query}"
                ),
            },
        ],
    )

    answer = response.choices[0].message.content
    sources = _format_sources(retrieved_chunks, _cited_numbers(answer))
    if not sources:
        return answer
    return f"{answer}\n\n---\n**Sources**\n{sources}"


if __name__ == "__main__":
    from retriever import retrieve

    question = (
        "What are the best dorms if I'm a senior writing a thesis and need a "
        "quieter dorm?"
    )
    print(f"Q: {question}\n")
    print(generate_response(question, retrieve(question)))
