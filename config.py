from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # OpenAI API Configuration
    openai_api_key: str = ""
    
    # Application Configuration
    app_name: str = "LLM Chatbot with RAG"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Vector Store Configuration
    vector_store_path: str = "./chroma_db"
    collection_name: str = "documents"
    
    # LLM Configuration
    llm_model: str = "gpt-3.5-turbo"
    embedding_model: str = "text-embedding-ada-002"
    temperature: float = 0.7
    max_tokens: int = 500
    
    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
