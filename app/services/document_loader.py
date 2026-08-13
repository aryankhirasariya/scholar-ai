import pdfplumber
import docx


def load_pdf(path: str) -> str:
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts)

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap  # step back for overlap
    return chunks

def load_docx(path: str) -> str:
    document = docx.Document(path)
    return "\n".join(p.text for p in document.paragraphs)


def load_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def load_document(path: str, source_type: str) -> str:
    if source_type == "pdf":
        return load_pdf(path)
    elif source_type == "docx":
        return load_docx(path)
    elif source_type == "txt":
        return load_txt(path)
    else:
        raise ValueError(f"Unsupported document type: {source_type}")


