"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    app_name: str = "AI Agent Platform"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # 数据库配置
    database_url: str = "sqlite:///./ai_agent_platform.db"
    
    # JWT配置
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Admin账号配置
    admin_username: str = "admin"
    admin_email: str = "admin@example.com"
    admin_password: str = "admin123"
    
    # AI模型默认配置
    default_model_name: str = "gpt-5"
    default_temperature: float = 0.7
    default_max_tokens: int = 2000
    
    # OpenAI配置
    openai_api_key: str = "sk-p5AmVKF2bJhWseY2e5aYWMNOafbTmuykXCWteIKuUfYCcmWp"
    openai_base_url: str = "https://linjinpeng-veloera.hf.space/v1"
    
    # CORS配置
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
