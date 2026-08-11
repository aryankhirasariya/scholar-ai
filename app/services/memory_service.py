import chromadb
import ollama

from app.config import settings

_client = chromadb.PersistentClient(path=settings.chroma_dir)
_collection = _client.get_or_create_collection(
    name="scholar_documents",
    metadata={"hnsw:space": "cosine"},
)


def embed_text(text: str) -> list[float]:
    response = ollama.embeddings(model=settings.embed_model, prompt=text)
    return response["embedding"]


def store_chunks(doc_id: str, filename: str, source_type: str, chunks: list[str]) -> int:
    if not chunks:
        return 0

    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    embeddings = [embed_text(chunk) for chunk in chunks]
    metadatas = [
        {"doc_id": doc_id, "filename": filename, "source_type": source_type}
        for _ in chunks
    ]

    _collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )
    return len(chunks)

def delete_document(doc_id: str) -> int:
    """
    Removes all chunks belonging to a document from persistent memory.
    Returns how many chunks were deleted.
    """
    existing = _collection.get(where={"doc_id": doc_id})
    ids_to_delete = existing.get("ids", [])

    if not ids_to_delete:
        return 0

    _collection.delete(ids=ids_to_delete)
    return len(ids_to_delete)

def search_memory(query: str, top_k: int = 5) -> list[dict]:
    query_embedding = embed_text(query)

    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    hits = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc_text, meta, distance in zip(docs, metas, distances):
        hits.append({
            "chunk_text": doc_text,
            "doc_id": meta.get("doc_id"),
            "filename": meta.get("filename"),
            "score": 1 - distance,
        })
    return hits


def list_documents() -> list[dict]:
    all_items = _collection.get()
    seen = {}
    for meta in all_items.get("metadatas", []):
        doc_id = meta.get("doc_id")
        if doc_id not in seen:
            seen[doc_id] = {
                "doc_id": doc_id,
                "filename": meta.get("filename"),
                "source_type": meta.get("source_type"),
                "chunk_count": 0,
            }
        seen[doc_id]["chunk_count"] += 1
    return list(seen.values())