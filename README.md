# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

This Unofficial Guide will be centered around on-campus housing. Student testimonies can be much more accurate in depicting living experiences in specific dorms than official channels. Facilities quality and social scene are just a few consequential factors that are usually learned through word of mouth.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | The Amherst Student | An article reviewing laundry rooms on campus. | https://amherststudent.com/article/cleaning-up-we-take-a-quick-spin-through-the-four/ |
| 2 | The Amherst Student | An article where writer Shane Dillon '26 expresses gratitude for his time living in Lipton House. | https://amherststudent.com/article/thank-you-lipton/ |
| 3 | prked.com | A student's unofficial guide reviewing first-year and upperclassman dorms, covering quiet vs. social atmosphere, facilities, and location. | https://prked.com/post/a-students-unofficial-guide-to-the-best-dorms-at-amherst-college |
| 4 | r/amherstcollege | A Reddit thread comparing and ranking dorms. | https://www.reddit.com/r/amherstcollege/comments/1shgint/best_and_worst_dorms/ |
| 5 | The Amherst Student | An article where writer Brenda Tenorio '27 reflects on the experience of living in Cohan Hall. | https://amherststudent.com/article/satire-why-cohan-needs-its-one-room-doubles/ |
| 6 | amherst.edu | A page listing all of the current theme and language communities on campus. | https://www.amherst.edu/campuslife/housing-dining/residential-life/theme |
| 7 | amherst.edu | A page listing all the residential area groups and the housing accommodations provided in some of them. | https://www.amherst.edu/campuslife/housing-dining/residential-life/residential-areas |
| 8 | The Amherst Student | An article describing the old room draw process, revealing desirable dorms. | https://amherststudent.amherst.edu/article/2016/04/13/room-draw-chaos.html |
| 9 | The Amherst Student | An article revealing the realities of campus social life and gatherings after the destruction of "the socials". | https://amherststudent.amherst.edu/article/2017/04/11/scattering-campus-social-life.html |
| 10 | College Confidential | A forum thread discussing the best freshman dorms and living on "the hill". | https://talk.collegeconfidential.com/t/dorms/473186 |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 900 characters

**Overlap:** 150 characters

**Why these choices fit your documents:** The sources I selected vary in structure (i.e. news articles, forum thread comments, and official webpages). Forum comments are naturally self-contained chunks that average 100-250 words. The articles use a larger paragraph structure where each paragraph covers one idea. The chunk size is bounded by my embedding model: `all-MiniLM-L6-v2` truncates input at 256 tokens, so a larger chunk would have its second half silently dropped before embedding (a 2400-char chunk tokenizes to ~512 tokens). 900 characters tops out around ~240 tokens, under the 256-token cap. That size still captures roughly one full comment or a single article paragraph — small enough that a chunk's embedding represents one dorm/opinion rather than blending several, which sharpens retrieval. The 150-character overlap prevents splitting a student's opinion from the dorm name they reference, which may appear at the start or end of a thought.

**Update — section-aware chunking for structured list pages:** The sliding window above suits prose, but the two amherst.edu pages (residential areas, theme communities) are lists, not paragraphs. A fixed window lumped unrelated sections together so the embedding for some chunks scored higher in distance, even if the the chunk contained the info needed for a query. For pages whose source is `amherst.edu`, `chunk_document()` now splits the body into sections instead: it breaks on blank lines and attaches each short heading line (or any line ending in `:`) to the list that follows it, so each housing section becomes its own focused chunk. These sections use a lower minimum length (20 chars) so meaningful short lists aren't dropped, and a section longer than the chunk size still falls back to the sliding window.

**Final chunk count:** 94

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`

**Production tradeoff reflection:** For deployment to real users with no cost constraint, I would consider using OpenAI's `text-embedding-3-large` which is a larger model that produces higher-dimensional vectors with higher accuracy on nuanced opinion text. Aside from cost, the tradeoffs include latency from network calls and the need for an API key. For a document pool this small, the accuracy gain is likely not worth the added complexity.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** "You are The Unofficial Guide, an assistant that answers questions about on-campus housing at Amherst College using real student testimonies and articles. Follow these rules strictly:
1. Answer USING ONLY the numbered sources provided in the context below. Do not use any outside knowledge about Amherst, its dorms, or campus life. If the sources disagree, present the different perspectives rather than picking one.
2. Ground every claim. After each claim, cite the source(s) it came from using ONLY the bracketed source numbers shown in the context, e.g. [1] or [2][3]. Never cite names, usernames, or anything other than those numbers. If several numbered sources say the same thing, cite each relevant number.
3. If the provided sources do not contain enough information to answer the question, say so plainly ("The sources I have don't cover that") instead of guessing. Do NOT mention a dorm unless it appears in the sources.
4. Keep the tone helpful and conversational, like an upperclassman giving honest advice — but every specific fact must trace back to a source.

**How source attribution is surfaced in the response:** When retrieved chunks are formatted into the prompt context, `_format_context()` numbers them per unique document rather than per chunk. Chunks from one forum thread or article share a single `[n]`, and each block is headed `[n] Title (Source)`. The system prompt instructs the model to cite every claim using the bracketed numbers and nothing else. After the model answers, `_cited_numbers()` extracts the `[n]` markers the model actually used with a regex, and `_format_sources()` builds a deduplicated **Sources** list containing only the documents that were actually cited. This was implemented to address the duplicate citations in the LLM's response. Each entry is rendered as `[n] Title — URL` so the user can follow any in-text citation back to the original student testimony or article. `generate_response()` appends this list under a `--- **Sources**` divider

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What are the best and worst dorms if I'm looking for a quieter environment? | Wieland, Morrow, or any of the Greenway dorms. Avoid dorms known to be party dorms (i.e. Hitchcock, Mayo-Smith, Seelye). | Sources don't explicitly mention best/worst for quieter environments. However, you might want to avoid dorms described as social hubs like Newport. | Partially relevant | Partially accurate |
| 2 | What dorms should I avoid if I don't have a bike or car and can't commute long distances? | Avoid dorms in North Campus (Plimpton, Marsh, and Tyler) or West Campus (Hitchcock, Chapman, and Seligman). | Tyler, Plimpton, Seligman. | Relevant | Accurate |
| 3 | Is living in Cohan really that bad? | While students have long complained about its confusing architecture, cramped living conditions, and poor facilities, students also describe it as a "rite of passage" that can bring you closer to those you live with. | Cohan has its downsides, but it's also seen as a character-building experience. | Relevant | Accurate |
| 4 | Where should I live if I don't want to fight for a washer and dryer while doing laundry? | Moore or Charles Drew which have a good student to washer/dryer ratio. | (Charles) Drew | Relevant | Accurate |
| 5 | Which dorm has a women's floor and the best facilities? | Nicholls Biondi is a great option that has two women's floors. It's in the Greenways which is a newer building so most rooms have AC and other nice facilities. | Nicholls Biondi has a women's floor. But Charles Pratt, James, and Stearns have the best/newest facilities. | Relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** Should I avoid the Triangle dorms?

**What the system returned:** The sources I have don't mention "triangle dorms" specifically.

**Root cause (tied to a specific pipeline stage):** While there are a few source documents that do mention the Triangle, the chunks that contain this information are out-ranked from the top 8 retrieved chunks. At the embedding stage, `all-MiniLM-L6-v2` mean-pools its token vectors so the only distinct word "Triangle" is averaged together with high-frequency filler ("should," "avoid," "the," "dorms") and its signal is diluted. "dorms" matches nearly every chunk in the corpus generically, so it pulls up off-topic dorm-ranking chatter. Querying "Should I avoid the Triangle houses?" actually returns a relevant response since the source text literally reads "Triangle houses," giving the word "houses" a meaning boost that "dorms" never gets.

**What you would change to fix it:** The max distance filter of 0.7 in `retrieve()` isn't the cause as the chunks do have distance scores below this cap. The simplest fix would be to raise top-k to around 10–12. A more robust fix would be to use query expansion (i.e. expanding "Triangle dorms" to also include "Triangle houses / Mayo-Smith / Hitchcock / Seelye") which would bridge the dorm/houses vocabulary gap before retrieval runs.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** The spec was helpful in walking me through all the design decisions that needed to be made beforehand in an order that made sense and built upon previous sections. It forced me to go into detail on certain aspects of the project that resulted in a robust document I could provide as context for the AI tool during the implementation stage.

**One way your implementation diverged from the spec, and why:** One way my implementation diverged from the spec was in the chunking strategy. Initially it was set to a fixed size method with a 900-character sliding window with overlap. While this was used for most documents, two documents (the amherst.edu pages containing sparse lists) were split on blank lines and with a lower character minimum. While The uniform window was simple and suitable for longer paragraph structures and prose, it ended up lumping unrelated sections of these sparser lists into one chunk. For example, a query that asked about women's floors was unable to produce results, even though the information was provided in one of these larger list chunks. Since this chunk was embedded with all of this extra noise on different topics, it scored poorly in distance. Section-aware splitting in the source-conditional `_split_sections()` gave each section/individual list its own focused embedding.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* I gave Claude the Documents table and my Chunking Strategy section and asked it to implement `ingest.py` containing `collect_documents()` which scrapes all 10 URLs using the tools described in the architecture and `chunk_documents()` to load, clean, and split the text into chunks ready for embedding (also containing metadata like chunk_id). 
- *What it produced:* It returned the two functions using a fixed character split with chunk size 400 tokens, which is about 2400 characters. 
- *What I changed or overrode:* I overrode the chunk size from 2400 characters to be 900 characters because I realized that (1) the embedding model I used had an input cap at 256 tokens, so a larger chunk would have its second half silently dropped and (2) my documents were not as large as I initially thought and the forum comments/news articles contained less characters than I expected.

**Instance 2**

- *What I gave the AI:* I gave Claude my Evaluation Plan section, the retrieve() output format, and the pipeline architecture diagram. I asked it to implement `generator.py` with `generate_response()` which formats the retrieved chunks to a system prompt that instructs the LLM to produce a grounded, cited answer. I also asked it to implement `app.py` which is the Gradio chat interface that wires the full pipeline together.
- *What it produced:* It returned both files for generating a response from the relevant chunks with a numbered list containing a citation for ever retrieved chunk, including sources that weren't actually referenced in the answer.
- *What I changed or overrode:* I overrode the citations to be keyed per unique document with `_document_numbers()` assigning one number per source in first-appearance order and to include only the numbers the model actually cited in its answer with `_cited_numbers()` and `_format_sources()`.
