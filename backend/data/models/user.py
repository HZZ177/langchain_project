"""
用户数据模型
"""
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, func, text
from backend.data.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=text("datetime('now', 'localtime')"))
    updated_at = Column(DateTime, server_default=text("datetime('now', 'localtime')"), onupdate=text("datetime('now', 'localtime')"))
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
