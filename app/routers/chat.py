from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse, SourceChunk
from app.services.memory_service import search_memory
from app.services.llm_service import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    hits = search_memory(request.question, top_k=request.top_k)

    
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