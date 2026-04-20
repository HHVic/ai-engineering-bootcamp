"""项目配置管理"""
import os
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # OpenAI API 配置（支持本地 Ollama）
    openai_api_key: str = "ollama"
    openai_api_base: str = "http://127.0.0.1:11434/v1"
    openai_model: str = "qwen2.5:7b"
    
    # 其他 API 密钥（可选）
    weather_api_key: str = ""
    
    # 缓存配置
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 缓存有效期（秒）
    
    # 对话配置
    max_history_messages: int = 10
    max_iterations: int = 5  # 防止无限递归
    
    # 日志配置
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """获取单例配置"""
    return Settings()
