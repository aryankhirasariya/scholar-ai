import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.memory_service import store_chunks, list_documents, delete_document
from app.services.auth_service import get_current_user
from app.config import settings
from app.models.schemas import UploadResponse, DocumentInfo
from app.services.document_loader import load_document, chunk_text

router = APIRouter(prefix="/documents", tags=["documents"])

EXT_MAP = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".txt": "txt",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
}


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    ext = os.path.splitext(file.filename)[1].lower()
    source_type = EXT_MAP.get(ext)

    if source_type is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Supported: pdf, docx, txt, png, jpg, jpeg",
        )

    os.makedirs(settings.upload_dir, exist_ok=True)
    doc_id = str(uuid.uuid4())
    save_path = os.path.join(settings.upload_dir, f"{doc_id}{ext}")

    with open(save_path, "wb") as f:
        f.write(await file.read())

    text = load_document(save_path, source_type)

    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail="Could not extract any text from this file.",
        )

    chunks = chunk_text(text)
    chunks_stored = store_chunks(
        doc_id=doc_id,
        filename=file.filename,
        source_type=source_type,
        chunks=chunks,
    )

    return UploadResponse(
        filename=file.filename,
        doc_id=doc_id,
        chunks_stored=chunks_stored,
        source_type=source_type,
    )


@router.get("/", response_model=list[DocumentInfo])
async def get_all_documents(
    current_user: dict = Depends(get_current_user)
):
    return list_documents()


@router.delete("/{doc_id}")
async def remove_document(
    doc_id: str,
    current_user: dict = Depends(get_current_user)
):
    deleted_count = delete_document(doc_id)

    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"doc_id": doc_id, "chunks_deleted": deleted_count}