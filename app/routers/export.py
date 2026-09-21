import io
from typing import List, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.export_service import generate_pdf, generate_docx
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/export", tags=["export"])


class ExportSection(BaseModel):
    question: str
    answer: str
    sources: Optional[List[str]] = None


class ExportRequest(BaseModel):
    title: Optional[str] = "Scholar AI Report"
    format: str  # "pdf" or "docx"
    sections: List[ExportSection]


@router.post("/")
def export_report(body: ExportRequest, user: dict = Depends(get_current_user)):
    sections = [s.dict() for s in body.sections]

    if body.format == "docx":
        content = generate_docx(body.title, sections)
        media_type = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        filename = "scholar-ai-report.docx"
    else:
        content = generate_pdf(body.title, sections)
        media_type = "application/pdf"
        filename = "scholar-ai-report.pdf"

    return StreamingResponse(
        io.BytesIO(content),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
