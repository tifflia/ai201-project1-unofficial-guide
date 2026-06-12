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

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

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

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

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

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
