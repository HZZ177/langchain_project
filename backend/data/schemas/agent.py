"""
Agent相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class AgentBase(BaseModel):
    """Agent基础模型"""
    name: str
    type: str
    description: Optional[str] = None


class AgentCreate(AgentBase):
    """Agent创建模型"""
    is_system: bool = True


class AgentUpdate(BaseModel):
    """Agent更新模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AgentResponse(AgentBase):
    """Agent响应模型"""
    id: int
    is_system: bool
    is_active: bool
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# QA Agent配置模型
class QAAgentConfigBase(BaseModel):
    """QA Agent配置基础模型"""
    model_name: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    api_key: str
    base_url: str = "https://linjinpeng-veloera.hf.space/v1"
    system_prompt: Optional[str] = None
    max_conversation_rounds: int = 5


class QAAgentConfigCreate(QAAgentConfigBase):
    """QA Agent配置创建模型"""
    agent_id: int


class QAAgentConfigUpdate(BaseModel):
    """QA Agent配置更新模型"""
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    system_prompt: Optional[str] = None
    max_conversation_rounds: Optional[int] = None


class QAAgentConfigResponse(QAAgentConfigBase):
    """QA Agent配置响应模型"""
    id: int
    agent_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Brainstorm Agent配置模型
class BrainstormAgentConfigBase(BaseModel):
    """Brainstorm Agent配置基础模型"""
    # 模型A配置
    model_a_name: str = "gpt-4"
    model_a_temperature: float = 0.7
    model_a_api_key: str
    model_a_base_url: str = "https://linjinpeng-veloera.hf.space/v1"
    model_a_system_prompt: Optional[str] = None

    # 模型B配置
    model_b_name: str = "claude-3-sonnet"
    model_b_temperature: float = 0.7
    model_b_api_key: str
    model_b_base_url: str = "https://api.anthropic.com/v1"
    model_b_system_prompt: Optional[str] = None

    # 讨论配置
    max_discussion_rounds: int = 5
    discussion_style: str = "collaborative"  # 'collaborative' 或 'debate'
    enable_summary: bool = True
    summary_prompt: Optional[str] = None


class BrainstormAgentConfigCreate(BrainstormAgentConfigBase):
    """Brainstorm Agent配置创建模型"""
    agent_id: int


class BrainstormAgentConfigUpdate(BaseModel):
    """Brainstorm Agent配置更新模型"""
    # 模型A配置
    model_a_name: Optional[str] = None
    model_a_temperature: Optional[float] = None
    model_a_api_key: Optional[str] = None
    model_a_base_url: Optional[str] = None
    model_a_system_prompt: Optional[str] = None

    # 模型B配置
    model_b_name: Optional[str] = None
    model_b_temperature: Optional[float] = None
    model_b_api_key: Optional[str] = None
    model_b_base_url: Optional[str] = None
    model_b_system_prompt: Optional[str] = None

    # 讨论配置
    max_discussion_rounds: Optional[int] = None
    discussion_style: Optional[str] = None
    enable_summary: Optional[bool] = None
    summary_prompt: Optional[str] = None


class BrainstormAgentConfigResponse(BrainstormAgentConfigBase):
    """Brainstorm Agent配置响应模型"""
    id: int
    agent_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
