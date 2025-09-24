"""
应用配置管理
"""
from typing import List, Optional


class Settings:
    """应用配置类 - 简化版，只使用硬编码默认值"""

    def __init__(self):
        # 应用基础配置
        self.app_name: str = "AI Agent Platform"
        self.app_version: str = "1.0.0"
        self.debug: bool = True

        # 数据库配置
        self.database_url: str = "sqlite:///./ai_agent_platform.db"

        # JWT配置
        self.secret_key: str = "hsyhgiewomflkzdnbgjgerhwluitojqaolwfmcnbhioeswgjh"
        self.algorithm: str = "HS256"
        self.access_token_expire_minutes: int = 30
        self.refresh_token_expire_days: int = 7

        # Admin账号配置
        self.admin_username: str = "admin"
        self.admin_email: str = "admin@example.com"
        self.admin_password: str = "admin123"

        # CORS配置
        self.allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]




# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
