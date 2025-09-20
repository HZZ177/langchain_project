"""
会话和对话数据模型
"""
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Text, func, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.data.database import Base


class Session(Base):
    """会话表"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    name = Column(String(200), default='新对话')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", backref="sessions")
    agent = relationship("Agent", backref="sessions")
    
    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, agent_id={self.agent_id}, name='{self.name}')>"


class Conversation(Base):
    """对话表"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    message_type = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    extra_data = Column(JSON)  # 存储额外信息
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    session = relationship("Session", backref="conversations")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, session_id={self.session_id}, type='{self.message_type}')>"
