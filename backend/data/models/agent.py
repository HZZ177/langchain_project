"""
Agent数据模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, func, ForeignKey
from sqlalchemy.orm import relationship
from backend.data.database import Base


class Agent(Base):
    """Agent表"""
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # 'qa_agent', 'brainstorm_agent'
    description = Column(Text)
    is_system = Column(Boolean, default=True)  # 系统预设或用户自定义
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    creator = relationship("User", backref="created_agents")
    config = relationship("AgentConfig", back_populates="agent", uselist=False)

    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', type='{self.type}')>"


class AgentConfig(Base):
    """Agent配置表"""
    __tablename__ = "agent_configs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, unique=True)

    # AI模型配置
    model_name = Column(String(100), nullable=False, default="gpt-3.5-turbo")
    temperature = Column(Float, nullable=False, default=0.7)
    max_tokens = Column(Integer, nullable=True)  # None表示无限制
    api_key = Column(Text, nullable=False)
    base_url = Column(String(200), nullable=False, default="https://api.openai.com/v1")

    # Agent特定配置
    system_prompt = Column(Text, nullable=True)
    max_conversation_rounds = Column(Integer, nullable=False, default=5)  # 最大对话轮数

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    agent = relationship("Agent", back_populates="config")

    def __repr__(self):
        return f"<AgentConfig(agent_id={self.agent_id}, model='{self.model_name}')>"
