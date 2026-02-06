from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """应用配置类，从环境变量加载配置"""
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./subtitles.db"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery配置
    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = REDIS_URL
    
    # JWT配置
    SECRET_KEY: str = "subtitle-api-secret-key-2023"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Whisper配置
    WHISPER_MODEL_PATH: str = "./models"
    WHISPER_MODEL: str = "base"
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 50000000  # 50MB
    
    # API配置
    API_PREFIX: str = "/api"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保上传目录和模型目录存在
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.WHISPER_MODEL_PATH).mkdir(parents=True, exist_ok=True)


# 创建全局配置实例
settings = Settings()