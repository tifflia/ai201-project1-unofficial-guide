import gradio as gr

from ingest import chunk_documents
from retriever import embed_and_store, get_collection, retrieve
from generator import generate_response, debug_report


# ---------------------------------------------------------------------------
# Ingestion — runs once on startup
# ---------------------------------------------------------------------------

def run_ingestion():
    """Load documents, chunk them, and store them in ChromaDB.

    If the vector store is already populated, ingestion is skipped. To
    re-ingest (e.g. after changing the chunking strategy or adding documents),
    delete the ./chroma_db folder and restart the app.
    """
    collection = get_collection()

    if collection.count() > 0:
        print(
            f"Vector store already populated ({collection.count()} chunks). "
            "Skipping ingestion."
        )
        print("To re-ingest, delete the ./chroma_db folder and restart.")
        return

    print("Ingesting documents...")
    chunks = chunk_documents()
    if chunks:
        embed_and_store(chunks)
        print(f"Ingestion complete. {len(chunks)} chunks stored.")
    else:
        print(
            "\n⚠️  No chunks produced. Run `python ingest.py collect` to fetch "
            "documents first.\n"
        )


# ---------------------------------------------------------------------------
# Chat handler
# ---------------------------------------------------------------------------

def chat(message, history):
    if not message.strip():
        return ""
    retrieved = retrieve(message)
    answer = generate_response(message, retrieved)
    # Full retrieval goes to the console for debugging; the user only sees the
    # cited-only answer that generate_response() returns.
    print(debug_report(message, retrieved, answer))
    return answer


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

with gr.Blocks(
    theme=gr.themes.Soft(primary_hue="purple"),
    title="The Unofficial Guide",
) as demo:

    gr.HTML("""
        <div style="text-align:center; padding:1.25rem 0 0.5rem;">
            <h1 style="font-size:2rem; font-weight:700; color:#581c87; margin:0;">
                🏠 The Unofficial Guide
            </h1>
            <p style="color:#6b7280; font-size:1rem; margin:0.4rem 0 0;">
                Honest, student-sourced advice on Amherst College housing.
            </p>
        </div>
    """)

    with gr.Row():
        with gr.Column(scale=3):
            gr.ChatInterface(
                fn=chat,
                type="messages",
                chatbot=gr.Chatbot(
                    height=440,
                    type="messages",
                    placeholder=(
                        "<div style='text-align:center; color:#9ca3af; margin-top:3rem;'>"
                        "Ask about a dorm, residential area, or campus life to get started 🛏️"
                        "</div>"
                    ),
                ),
                textbox=gr.Textbox(
                    placeholder='e.g. "Is living in Cohan really that bad?"',
                    container=False,
                    scale=7,
                ),
                examples=[
                    "What are the best and worst dorms if I'm looking for a quieter environment?",
                    "What dorms should I avoid if I don't have a bike or car and can't commute long distances?",
                    "Is living in Cohan really that bad?",
                    "Where should I live if I don't want to fight for a washer and dryer while doing laundry?",
                    "Which dorm has a women's floor and the best facilities?",
                ],
                cache_examples=False,
            )

        with gr.Column(scale=1, min_width=180):
            gr.HTML("""
                <style>
                    /* Fixed light background, so force readable text colors in
                       both light and dark themes (Gradio's dark mode otherwise
                       overrides these to white, making them vanish). */
                    .guide-sources { background:#faf5ff; border:1px solid #e9d5ff;
                        border-radius:10px; padding:1rem; margin-top:0.5rem; }
                    .guide-sources .gs-head { font-size:0.8rem; font-weight:700;
                        color:#581c87 !important; margin:0 0 0.5rem; letter-spacing:0.05em; }
                    .guide-sources ul { font-size:0.85rem; list-style:none;
                        padding:0; margin:0; line-height:1.8; }
                    .guide-sources li { color:#6b21a8 !important; }
                    .guide-sources hr { border:none; border-top:1px solid #e9d5ff; margin:0.75rem 0; }
                    .guide-sources .gs-note { font-size:0.75rem; color:#7c3aed !important;
                        margin:0; line-height:1.5; }
                </style>
                <div class="guide-sources">
                    <p class="gs-head">📚 WHERE ANSWERS COME FROM</p>
                    <ul>
                        <li>📰 The Amherst Student</li>
                        <li>👥 r/amherstcollege</li>
                        <li>🅿️ prked.com guide</li>
                        <li>🏛️ amherst.edu housing pages</li>
                        <li>💬 College Confidential</li>
                    </ul>
                    <hr>
                    <p class="gs-note">
                        Answers are grounded in these sources only and cite where
                        each claim comes from. If the sources don't cover your
                        question, the guide will say so.
                    </p>
                </div>
            """)


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  The Unofficial Guide — starting up")
    print("=" * 50 + "\n")
    run_ingestion()
    demo.launch()
