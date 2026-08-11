- **Backend:** FastAPI (Python)
- **LLM:** Ollama running Llama 3.1 locally
- **Embeddings:** Ollama running nomic-embed-text
- **Vector database:** ChromaDB (persistent, local)
- **Document parsing:** pdfplumber (PDF), python-docx (Word)
- **OCR:** Tesseract via pytesseract
- **Frontend:** Vanilla HTML/CSS/JS (no framework, served directly by FastAPI)

## Setup

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com) installed
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed (Windows) or via package manager (Mac/Linux)

### Installation

```bash
# Clone the repo
git clone https://github.com/aryankhirasariya/scholar-ai.git
cd scholar-ai

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Pull the required local models
ollama pull llama3.1
ollama pull nomic-embed-text

# Copy environment config
copy .env.example .env      # Windows
cp .env.example .env        # Mac/Linux
```

### Running

```bash
uvicorn app.main:app --reload
```

- **Web UI:** http://127.0.0.1:8000/app
- **API docs:** http://127.0.0.1:8000/docs

## Project structure

scholar-ai/
├── app/
│ ├── main.py # FastAPI app entry point
│ ├── config.py # Settings loaded from .env
│ ├── models/schemas.py # Request/response data shapes
│ ├── routers/
│ │ ├── documents.py # Upload, list, delete endpoints
│ │ └── chat.py # RAG chat endpoint
│ ├── services/
│ │ ├── document_loader.py # PDF/DOCX/TXT reading + chunking
│ │ ├── ocr_service.py # Image → text extraction
│ │ ├── memory_service.py # ChromaDB storage + retrieval
│ │ └── llm_service.py # Ollama chat generation
│ └── static/index.html # Frontend
├── data/
│ ├── uploads/ # Uploaded files (gitignored)
│ └── chroma_db/ # Vector database (gitignored)
└── requirements.txt


## Project context

Built for CE0727 - Software Group Project, Indus Institute of Technology & Engineering, Computer Science & Engineering Department.