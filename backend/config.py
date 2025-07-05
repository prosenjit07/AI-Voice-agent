import os
from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Audio Configuration
    input_sample_rate: int = 16000
    output_sample_rate: int = 24000
    audio_format: str = "pcm"
    channels: int = 1
    chunk_size: int = 512
    
    # Gemini Configuration
    gemini_model: str = "gemini-2.0-flash-live-preview-04-09"
    gemini_voice: str = "Aoede"
    max_session_duration: int = 600  # 10 minutes
    
    # RTVI Configuration
    rtvi_version: str = "0.2.0"
    enable_interruptions: bool = True
    enable_metrics: bool = True
    
    # WebSocket Configuration
    websocket_timeout: int = 30
    max_connections: int = 100
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    """Get cached settings instance"""
    return Settings()
