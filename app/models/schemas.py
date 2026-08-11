from pydantic import BaseModel
from typing import List


class UploadResponse(BaseModel):
    filename: str
    doc_id: str
    chunks_stored: int
    source_type: str  # "pdf" | "docx" | "txt" | "image"


class ChatRequest(BaseModel):
    session_id: str
    question: str
    top_k: int = 5


class SourceChunk(BaseModel):
    doc_id: str
    filename: str
    chunk_text: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    source_type: str
    chunk_count: int