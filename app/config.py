from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_host: str = "http://localhost:11434"
    llm_model: str = "llama3.1"
    embed_model: str = "nomic-embed-text"
    upload_dir: str = "data/uploads"
    chroma_dir: str = "data/chroma_db"

    class Config:
        env_file = ".env"


settings = Settings()