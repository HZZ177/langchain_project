"""
系统配置数据模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, text
from backend.data.database import Base


class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)  # 配置键
    value = Column(Text, nullable=True)  # 配置值（JSON字符串）
    description = Column(Text, nullable=True)  # 配置描述
    created_at = Column(DateTime, server_default=text("datetime('now', 'localtime')"))
    updated_at = Column(DateTime, server_default=text("datetime('now', 'localtime')"), onupdate=text("datetime('now', 'localtime')"))
    
    def __repr__(self):
        return f"<SystemConfig(key='{self.key}', value='{self.value[:50]}...')>"
