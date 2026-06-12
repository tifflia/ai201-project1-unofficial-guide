# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

This Unofficial Guide will be centered around on-campus housing. Student testimonies can be much more accurate in depicting living experiences in specific dorms than official channels. Facilities quality and social scene are just a few consequential factors that are usually learned through word of mouth.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | The Amherst Student | An article reviewing laundry rooms on campus. | https://amherststudent.com/article/cleaning-up-we-take-a-quick-spin-through-the-four/ |
| 2 | The Amherst Student | An article where writer Shane Dillon '26 expresses gratitude for his time living in Lipton House. | https://amherststudent.com/article/thank-you-lipton/ |
| 3 | r/amherstcollege | A Reddit thread where people mention some unexpected cons of student housing. | https://www.reddit.com/r/amherstcollege/comments/1ldaqtb/dorm_honest_review/ |
| 4 | r/amherstcollege | A Reddit thread comparing and ranking dorms. | https://www.reddit.com/r/amherstcollege/comments/1shgint/best_and_worst_dorms/ |
| 5 | The Amherst Student | An article where writer Brenda Tenorio '27 reflects on the experience of living in Cohan Hall. | https://amherststudent.com/article/satire-why-cohan-needs-its-one-room-doubles/ |
| 6 | amherst.edu | A page listing all of the current theme and language communities on campus. | https://www.amherst.edu/campuslife/housing-dining/residential-life/theme |
| 7 | amherst.edu | A page listing all the residential area groups and the housing accommodations provided in some of them. | https://www.amherst.edu/campuslife/housing-dining/residential-life/residential-areas |
| 8 | The Amherst Student | An article describing the old room draw process, revealing desirable dorms. | https://amherststudent.amherst.edu/article/2016/04/13/room-draw-chaos.html |
| 9 | The Amherst Student | An article revealing the realities of campus social life and gatherings after the destruction of "the socials". | https://amherststudent.amherst.edu/article/2017/04/11/scattering-campus-social-life.html |
| 10 | College Confidential | A forum thread discussing the best freshman dorms and living on "the hill". | https://talk.collegeconfidential.com/t/dorms/473186 |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 900 characters (≤256 tokens for this corpus)

**Overlap:** 150 characters

**Reasoning:** The sources I selected vary in structure (i.e. news articles, forum thread comments, and official webpages). Forum comments are naturally self-contained chunks that average 100-250 words. The articles use a larger paragraph structure where each paragraph covers one idea. The chunk size is bounded by my embedding model: `all-MiniLM-L6-v2` truncates input at 256 tokens, so a larger chunk would have its second half silently dropped before embedding (a 2400-char chunk tokenizes to ~512 tokens). 900 characters tops out around ~240 tokens, comfortably under the 256-token cap. That size still captures roughly one full comment or a single article paragraph — small enough that a chunk's embedding represents one dorm/opinion rather than blending several, which sharpens retrieval. The 150-character overlap prevents splitting a student's opinion from the dorm name they reference, which may appear at the start or end of a thought.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`

**Top-k:** 5

**Production tradeoff reflection:** For deployment to real users with no cost constraint, I would consider using OpenAI's `text-embedding-3-large` which is a larger model that produces higher-dimensional vectors with higher accuracy on nuanced opinion text. Aside from cost, the tradeoffs include latency from network calls and the need for an API key. For a document pool this small, the accuracy gain is likely not worth the added complexity.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What are the best dorms if I'm a senior writing a thesis? | Plimpton, Wieland, Morrow, Lipton. Avoid dorms in "the triangle" (i.e. Hitchcock, Mayo-Smith, Seelye). |
| 2 | What dorms should I avoid if I don't have a bike or car and can't commute long distances? | Avoid dorms in North Campus (Plimpton, Marsh, and Tyler) or West Campus (Hitchcock, Chapman, and Seligman). |
| 3 | Is living in Cohan really that bad? | While students have long complained about its confusing architecture, cramped living conditions, and poor facilities, students also describe it as a "rite of passage" that can bring you closer to those you live with. |
| 4 | Where should I live if I don't want to fight for a washer and dryer while doing laundry? | Moore. This dorm boasts a laundry room fitted with 4 washers and 4 dryers, as opposed to most dorms which only have half the amount. The hall also has an elevator, making the laundry room easily accessible. |
| 5 | What's the best dorm for me if I want to live in an all women's floor and have the best facilities? | Nicholls Biondi is a great option that has two women's floors. It's in the Greenways which is a newer building so most rooms have AC and other nice facilities. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Missing source attribution. Chunks may be retrieved in isolation and the context/attribution may be lost during ingestion. If the source metadata isn't explicitly attached to each chunk, it would be difficult to trace a claim back to its source and determine its validity. 

2. Inconsistent dorm coverage. There are only a few documents that have very detailed accounts of specific dorms, while most other dorms appear only incidentally. A query about an underrepresented dorm will retrieve loosely related chunks and the system might generate a confident answer from weak evidence.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
User query
    │
    ▼
[1] DOCUMENT INGESTION      ──► Reddit threads, articles, forum post
    ingest.py                   loaded via requests / BeautifulSoup
    │                           or Playwright for JavaScript-rendered sites.
    ▼
[2] CHUNKING                ──► Chunk extracted text from docs
    ingest.py                   900 chars / 150 overlap (≤256-token limit),
    │                           metadata attached
    ▼
[3] EMBEDDING + VECTOR STORE ──► all-MiniLM-L6-v2 (sentence-transformers),
    retriever.py                 ChromaDB persistent
    │
    ▼
[4] RETRIEVAL               ──► Query embedded, top-5 chunks returned
    retriever.py                by cosine similarity search
    │
    ▼
[5] GENERATION              ──► Groq (llama-3.3-70b-versatile)
    generator.py                chunks passed as context,
    │                           grounded answer with source citations
    ▼
UI response (Gradio chat interface - app.py)
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

I'll give Claude the Documents table (10 sources) and my Chunking Strategy section. I'll ask it to implement `ingest.py` containing `collect_documents()` which scrapes all 10 URLs using the tools described in the architecture and `chunk_documents()` which loads .txt files from /documents, cleans them, and splits the text into chunks ready for embedding (also containing metadata like chunk_id). To verify, both scripts will be run and write the resulting chunks to .txt files in /documents to first see that the collected text matches the sources and that no chunks contain HTML artifacts or nav boilerplate.

**Milestone 4 — Embedding and retrieval:**

I'll give Claude my Retrieval Approach section, the chunk output from Milestone 3, and the pipeline architecture diagram. I'll ask it to implement `retrieval.py` containing `embed_and_store()` which loads the chunks, generates embeddings using sentence-transformers, and stores them in a ChromaDB collection with source metadata. It'll also contain `retrieve()` which embeds a query string and returns the top-k most similar chunks with their distances and source attribution. To verify, I'll run a test query (possibly one of the questions from the Evaluation Plan) and check that the returned chunks are relevant. I'll check that none of the distance scores are over 0.7 (maybe filter out if so) and that the top 2 results are at least below 0.5.

**Milestone 5 — Generation and interface:**

I'll give Claude my Evaluation Plan section, the retrieve() output format, and the pipeline architecture diagram. I'll ask it to implement `generator.py` with `generate_response()` that formats the retrieved chunks to a system prompt that instructs the LLM to produce a grounded, cited answer. It should also implement `app.py` which is the Gradio chat interface that wires the full pipeline together. To verify, I'll run all 5 questions from the Evaluation Plan and compare the responses against expected answers. From there, I'll check to see whether any response cites a dorm not present in the retrieved chunks or give an unexpected response.