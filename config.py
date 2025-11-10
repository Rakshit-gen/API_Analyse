from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    groq_api_key: str
    model_name: str = "llama-3.3-70b-versatile"
    temperature: float = 0.1
    max_tokens: int = 2000
    port: int = 8000
    host: str = "0.0.0.0"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
