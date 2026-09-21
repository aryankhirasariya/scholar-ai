import chromadb
import ollama

from app.config import settings

_client = chromadb.PersistentClient(path=settings.chroma_dir)
_collection = _client.get_or_create_collection(
    name="scholar_documents",
    metadata={"hnsw:space": "cosine"},
)


def embed_text(text: str) -> list[float]:
    if len(text) > 4000:  # sanity cap, well under model's token limit
        text = text[:4000]
    response = ollama.embeddings(model=settings.embed_model, prompt=text)
    return response["embedding"]


def store_chunks(
    doc_id: str,
    filename: str,
    source_type: str,
    chunks: list[str],
    owner_id: int,
) -> int:
    if not chunks:
        return 0

    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    embeddings = [embed_text(chunk) for chunk in chunks]
    metadatas = [
        {
            "doc_id": doc_id,
            "filename": filename,
            "source_type": source_type,
            "owner_id": owner_id,
        }
        for _ in chunks
    ]

    _collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )
    return len(chunks)


def delete_document(doc_id: str, owner_id: int) -> int:
    """
    Removes all chunks belonging to a document from persistent memory,
    but only if it belongs to the requesting owner.
    Returns how many chunks were deleted.
    """
    existing = _collection.get(
        where={"$and": [{"doc_id": doc_id}, {"owner_id": owner_id}]}
    )
    ids_to_delete = existing.get("ids", [])

    if not ids_to_delete:
        return 0

    _collection.delete(ids=ids_to_delete)
    return len(ids_to_delete)


def search_memory(query: str, owner_id: int, top_k: int = 5) -> list[dict]:
    query_embedding = embed_text(query)

    # Find every unique document belonging to this owner
    all_items = _collection.get(
        where={"owner_id": owner_id},
        include=["metadatas"],
    )
    doc_ids = list({m["doc_id"] for m in all_items["metadatas"]})

    if not doc_ids:
        return []

    # Pull a fair share of chunks from EACH document
    per_doc_k = max(1, top_k // len(doc_ids))

    hits = []
    for doc_id in doc_ids:
        results = _collection.query(
            query_embeddings=[query_embedding],
            n_results=per_doc_k,
            where={"$and": [{"doc_id": doc_id}, {"owner_id": owner_id}]},
        )
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

    hits.sort(key=lambda x: x["score"], reverse=True)
    return hits


def list_documents(owner_id: int) -> list[dict]:
    all_items = _collection.get(where={"owner_id": owner_id})
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