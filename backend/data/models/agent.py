"""
Agent数据模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, func, ForeignKey, text
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
    created_at = Column(DateTime, server_default=text("datetime('now', 'localtime')"))
    updated_at = Column(DateTime, server_default=text("datetime('now', 'localtime')"), onupdate=text("datetime('now', 'localtime')"))

    # 关系 - 多态配置关系
    creator = relationship("User", backref="created_agents")
    qa_config = relationship("QAAgentConfig", back_populates="agent", uselist=False)
    brainstorm_config = relationship("BrainstormAgentConfig", back_populates="agent", uselist=False)

    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', type='{self.type}')>"


class QAAgentConfig(Base):
    """QA Agent专用配置表"""
    __tablename__ = "qa_agent_configs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, unique=True)

    # QA Agent配置
    model_name = Column(String(100), nullable=False, default="gemini-2.5-flash-preview-05-20")
    temperature = Column(Float, nullable=False, default=0.7)
    max_tokens = Column(Integer, nullable=True, default=None)  # None表示无限制
    api_key = Column(Text, nullable=False, default="sk-cvqWUuYL0c6Nw3gK9UH3TtGzfnUWyntiFtolbzw7sgFSWQQ2")
    base_url = Column(String(200), nullable=False, default="https://x666.me/v1")
    system_prompt = Column(Text, nullable=True, default="你是一个有用的AI助手，能够进行自然的中文对话。请提供准确、有帮助的回答。")
    max_conversation_rounds = Column(Integer, nullable=False, default=5)

    created_at = Column(DateTime, server_default=text("datetime('now', 'localtime')"))
    updated_at = Column(DateTime, server_default=text("datetime('now', 'localtime')"), onupdate=text("datetime('now', 'localtime')"))

    # 关系
    agent = relationship("Agent", back_populates="qa_config")

    def __repr__(self):
        return f"<QAAgentConfig(agent_id={self.agent_id}, model='{self.model_name}')>"


class BrainstormAgentConfig(Base):
    """Brainstorm Agent专用配置表"""
    __tablename__ = "brainstorm_agent_configs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, unique=True)

    # 模型A配置
    model_a_name = Column(String(100), nullable=False, default="gemini-2.5-flash-preview-05-20")
    model_a_temperature = Column(Float, nullable=False, default=0.7)
    model_a_api_key = Column(Text, nullable=False, default="sk-cvqWUuYL0c6Nw3gK9UH3TtGzfnUWyntiFtolbzw7sgFSWQQ2")
    model_a_base_url = Column(String(200), nullable=False, default="https://x666.me/v1")
    model_a_system_prompt = Column(Text, nullable=True, default="你是一个智能的讨论参与者，擅长提供深入的分析和独特的见解。")

    # 模型B配置
    model_b_name = Column(String(100), nullable=False, default="gemini-2.5-flash-preview-05-20")
    model_b_temperature = Column(Float, nullable=False, default=0.7)
    model_b_api_key = Column(Text, nullable=False, default="sk-cvqWUuYL0c6Nw3gK9UH3TtGzfnUWyntiFtolbzw7sgFSWQQ2")
    model_b_base_url = Column(String(200), nullable=False, default="https://x666.me/v1")
    model_b_system_prompt = Column(Text, nullable=True, default="你是一个善于思辨的讨论者，能够从不同角度审视问题并提供建设性观点。")

    # 讨论配置
    max_discussion_rounds = Column(Integer, nullable=False, default=5)
    discussion_style = Column(String(50), nullable=False, default='collaborative')  # 'collaborative' 或 'debate'
    enable_summary = Column(Boolean, nullable=False, default=True)
    summary_prompt = Column(Text, nullable=True, default="请对以上讨论进行客观全面的总结，包括主要观点、共识和分歧。")

    created_at = Column(DateTime, server_default=text("datetime('now', 'localtime')"))
    updated_at = Column(DateTime, server_default=text("datetime('now', 'localtime')"), onupdate=text("datetime('now', 'localtime')"))

    # 关系
    agent = relationship("Agent", back_populates="brainstorm_config")

    def __repr__(self):
        return f"<BrainstormAgentConfig(agent_id={self.agent_id}, model_a='{self.model_a_name}', model_b='{self.model_b_name}')>"
