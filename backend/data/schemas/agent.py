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


class AgentConfigBase(BaseModel):
    """Agent配置基础模型"""
    model_name: str = "gpt-5"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    api_key: str
    base_url: str = "https://linjinpeng-veloera.hf.space/v1"
    system_prompt: Optional[str] = None
    max_conversation_rounds: int = 5


class AgentConfigCreate(AgentConfigBase):
    """Agent配置创建模型"""
    agent_id: int


class AgentConfigUpdate(BaseModel):
    """Agent配置更新模型"""
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    system_prompt: Optional[str] = None
    max_conversation_rounds: Optional[int] = None


class AgentConfigResponse(AgentConfigBase):
    """Agent配置响应模型"""
    id: int
    agent_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
