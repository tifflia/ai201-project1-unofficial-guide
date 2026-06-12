import chromadb
from chromadb.utils import embedding_functions
from config import CHROMA_COLLECTION, CHROMA_PATH, EMBEDDING_MODEL, N_RESULTS

# Embedding function and ChromaDB client are initialized once at module load.
# sentence-transformers downloads the model on first use — this may take
# 30–60 seconds the very first time. Subsequent runs use a local cache.
_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    embedding_function=_ef,
    metadata={"hnsw:space": "cosine"},
)


def get_collection():
    """Return the ChromaDB collection. Used by app.py during ingestion."""
    return _collection


def embed_and_store(chunks):
    """
    Embed a list of chunks and store them in the vector database.

    _collection.add() takes three parallel lists built from the chunks
    returned by chunk_document():
      - documents : raw text strings — ChromaDB's embedding function converts
                    these to vectors automatically using sentence-transformers
      - metadatas : one dict per chunk, stored alongside the vector so that
                    retrieve() can surface which source a result came from.
                    We keep source, title, and url so attribution stays
                    attached to every chunk (see planning.md, Anticipated
                    Challenge #1).
      - ids       : the unique chunk_id strings used to identify each entry

    You don't generate embeddings manually here — you hand over the text
    and ChromaDB handles the vector math.
    """
    _collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[
            {
                "source": c["source"],
                "title": c["title"],
                "url": c["url"],
            }
            for c in chunks
        ],
        ids=[c["chunk_id"] for c in chunks],
    )
    print(f"Stored {_collection.count()} total chunks in the vector database.")


def retrieve(query, n_results=N_RESULTS):
    """
    Find the most relevant chunks for a user's question.

    Use _collection.query() to run a semantic search. It takes:
      - query_texts : a list containing your query string
      - n_results   : how many results to return
      - include     : what to return — use ["documents", "metadatas", "distances"]

    Returns a list of dicts, each with:
      - "text"     : the chunk text
      - "source"   : the source the chunk came from (from metadatas)
      - "title"    : the document title (from metadatas)
      - "url"      : the document url (from metadatas)
      - "distance" : the cosine distance (lower = more similar)

    _collection.query() returns nested lists (one per query). We only have one
    query, so we index [0] to get the actual results.
    """
    if _collection.count() == 0:
        return []

    results = _collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    chunks = [
        {
            "text": doc,
            "source": meta.get("source", ""),
            "title": meta.get("title", ""),
            "url": meta.get("url", ""),
            "distance": dist,
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]

    # Drop weak matches — see planning.md, Milestone 4 verification.
    chunks = [c for c in chunks if c["distance"] < 0.7]

    return chunks


if __name__ == "__main__":
    from ingest import chunk_documents

    # Rebuild from scratch so reruns don't pile up duplicate chunks.
    if _collection.count() > 0:
        _client.delete_collection(CHROMA_COLLECTION)
        _collection = _client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            embedding_function=_ef,
            metadata={"hnsw:space": "cosine"},
        )

    print("Loading and chunking documents...")
    chunks = chunk_documents()
    print("\nEmbedding and storing chunks...")
    embed_and_store(chunks)

    sample = "What are the best dorms if I'm a senior writing a thesis and need a quieter dorm?"
    print(f"\nSample query: {sample!r}\n")
    for chunk in retrieve(sample):
        preview = chunk["text"].replace("\n", " ")[:80]
        print(f"[{chunk['source']}] (dist: {chunk['distance']:.3f}) {preview}...")
