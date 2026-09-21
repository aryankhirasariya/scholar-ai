from pydantic import BaseModel, EmailStr
from typing import List, Optional


# ── EXISTING ──────────────────────────────────────────────

class UploadResponse(BaseModel):
    filename: str
    doc_id: str
    chunks_stored: int
    source_type: str

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


# ── AUTH ──────────────────────────────────────────────────

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    name: str
    email: str

class UserInfo(BaseModel):
    id: int
    name: str
    email: str