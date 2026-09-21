import pdfplumber
import docx
from app.services.ocr_service import load_image_text


def load_pdf(path: str) -> str:
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts)


def load_docx(path: str) -> str:
    document = docx.Document(path)
    return "\n".join(p.text for p in document.paragraphs)


def load_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def load_image(path: str) -> str:
    return load_image_text(path)


def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 150
) -> list[str]:
    # clean up excessive whitespace first
    import re
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    text = text.strip()

    chunks = []
    start  = 0
    while start < len(text):
        end = start + chunk_size

        # try to break at a sentence boundary
        if end < len(text):
            for punct in [".\n", ".\n\n", ". ", "\n\n", "\n"]:
                boundary = text.rfind(punct, start + 400, end)
                if boundary != -1:
                    end = boundary + len(punct)
                    break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap

    return chunks


def load_document(path: str, source_type: str) -> str:
    if source_type == "pdf":
        return load_pdf(path)
    elif source_type == "docx":
        return load_docx(path)
    elif source_type == "txt":
        return load_txt(path)
    elif source_type in ("image", "png", "jpg", "jpeg"):
        return load_image(path)
    else:
        raise ValueError(f"Unsupported document type: {source_type}")