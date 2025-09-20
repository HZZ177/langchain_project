"""
Agent数据模型
"""
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Text, func, ForeignKey
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
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', type='{self.type}')>"


class AgentDefaultConfig(Base):
    """Agent默认配置表"""
    __tablename__ = "agent_default_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    config_key = Column(String(100), nullable=False)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(20), default='string')  # 'string', 'number', 'boolean', 'json'
    description = Column(Text)
    is_sensitive = Column(Boolean, default=False)  # 是否为敏感信息
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    agent = relationship("Agent", backref="default_configs")
    
    def __repr__(self):
        return f"<AgentDefaultConfig(agent_id={self.agent_id}, key='{self.config_key}')>"


class UserAgentConfig(Base):
    """用户Agent配置表"""
    __tablename__ = "user_agent_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    config_key = Column(String(100), nullable=False)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(20), default='string')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", backref="agent_configs")
    agent = relationship("Agent", backref="user_configs")
    
    def __repr__(self):
        return f"<UserAgentConfig(user_id={self.user_id}, agent_id={self.agent_id}, key='{self.config_key}')>"
