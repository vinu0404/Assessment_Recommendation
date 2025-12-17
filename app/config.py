import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    OPENAI_TEMPERATURE: float = 0.2
    OPENAI_MAX_TOKENS: int = 2048
    SQLITE_DB_PATH: str = "./storage/sqlite/sessions.db"
    CHROMA_DB_PATH: str = "./storage/chroma"
    CHROMA_COLLECTION_NAME: str = "assessments"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = False
    API_WORKERS: int = 1
    CHAINLIT_HOST: str = "0.0.0.0"
    CHAINLIT_PORT: int = 8001
    REFRESH_API_KEY: str
    CORS_ORIGINS: str = "http://localhost:8001,http://localhost:3000"
    
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    SHL_CATALOG_URL: str = "https://www.shl.com/products/product-catalog/"
    SCRAPER_DELAY: float = 1.5
    SCRAPER_TIMEOUT: int = 30
    RAG_TOP_K: int = 15  
    RAG_SIMILARITY_THRESHOLD: float = 0.50  
    RAG_SIMILARITY_THRESHOLD_FALLBACK: float = 0.30  
    RAG_FINAL_SELECT_MIN: int = 3 
    RAG_FINAL_SELECT_MAX: int = 8
    RAG_ENABLE_LLM_RERANKING: bool = True   
    EMBEDDING_BATCH_SIZE: int = 20
    ENABLE_QUERY_EXPANSION: bool = True
    ASSESSMENTS_JSON_PATH: str = "./data/shl_assessments.json"
    TRAIN_SET_PATH: str = "./data/labeled_train_set.json"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra='ignore'
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            Path(self.SQLITE_DB_PATH).parent,
            Path(self.CHROMA_DB_PATH),
            Path(self.LOG_FILE).parent,
            Path(self.ASSESSMENTS_JSON_PATH).parent,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
settings = Settings()

settings.ensure_directories()