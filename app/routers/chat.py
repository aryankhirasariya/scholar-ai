from fastapi import APIRouter, Depends

from app.models.schemas import ChatRequest, ChatResponse, SourceChunk
from app.services.memory_service import search_memory
from app.services.llm_service import answer_question
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    hits = search_memory(request.question, owner_id=current_user["id"], top_k=request.top_k)

    answer = answer_question(request.question, hits)
    sources = [
        SourceChunk(
            doc_id=hit["doc_id"],
            filename=hit["filename"],
            chunk_text=hit["chunk_text"][:200] + "...",
            score=round(hit["score"], 3),
        )
        for hit in hits
    ]

    return ChatResponse(answer=answer, sources=sources)