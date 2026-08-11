import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    chroma_path: str = os.getenv("CHROMA_PATH", "./storage/chroma")
    collection_name: str = os.getenv("COLLECTION_NAME", "rag_chunks")
    default_chunk_size: int = int(os.getenv("DEFAULT_CHUNK_SIZE", "900"))
    default_chunk_overlap: int = int(os.getenv("DEFAULT_CHUNK_OVERLAP", "120"))
    default_top_k: int = int(os.getenv("DEFAULT_TOP_K", "5"))
    max_top_k: int = int(os.getenv("MAX_TOP_K", "20"))

settings = Settings()
