import ollama
from app.config import settings


def answer_question(question: str, hits: list[dict]) -> str:
    if not hits:
        context_block = "No relevant documents found."
    else:
        context_block = "\n\n---\n\n".join(
            f"[Source: {hit['filename']}]\n{hit['chunk_text']}"
            for hit in hits
        )

    system_prompt = (
        "You are Scholar AI, a research assistant. Answer the user's question "
        "using ONLY the context provided below. Each excerpt is labeled with its "
        "source document — always attribute claims to the correct source by name. "
        "If the context doesn't contain the answer, say so clearly instead of guessing."
    )

    user_prompt = f"Context:\n{context_block}\n\nQuestion: {question}"

    response = ollama.chat(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        options={
            "num_ctx": 8192  # raise context window so nothing gets silently truncated
        },
    )
    return response["message"]["content"]