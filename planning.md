# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

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

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

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

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
