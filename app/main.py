from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import documents, chat

app = FastAPI(
    title="Scholar AI",
    description="AI-powered research operating system",
    version="0.1.0",
)

app.include_router(documents.router)
app.include_router(chat.router)

app.mount("/app", StaticFiles(directory="app/static", html=True), name="static")


@app.get("/")
async def root():
    return {"message": "Scholar AI is running", "docs": "/docs", "ui": "/app"}