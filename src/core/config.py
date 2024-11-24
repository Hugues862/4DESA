from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "4DESA Project"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key"  # In production, use environment variable
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str
    
    # Azure Storage
    STORAGE_CONN_STRING: str
    STORAGE_CONTAINER: str
    
    # Media Settings
    ALLOWED_MEDIA_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif", "video/mp4"]
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings() 