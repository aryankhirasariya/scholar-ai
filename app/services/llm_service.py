import ollama
from app.config import settings


def answer_question(question: str, context_chunks: list[str]) -> str:
    context_block = "\n\n---\n\n".join(context_chunks) if context_chunks else "No relevant documents found."

    system_prompt = (
        "You are Scholar AI, a research assistant. Answer the user's question "
        "using ONLY the context provided below. If the context doesn't contain "
        "the answer, say so clearly instead of guessing."
    )

    user_prompt = f"Context:\n{context_block}\n\nQuestion: {question}"

    response = ollama.chat(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response["message"]["content"]