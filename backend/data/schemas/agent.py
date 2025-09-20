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
    config_key: str
    config_value: str
    config_type: str = "string"
    description: Optional[str] = None


class AgentConfigCreate(AgentConfigBase):
    """Agent配置创建模型"""
    agent_id: int


class AgentConfigUpdate(BaseModel):
    """Agent配置更新模型"""
    config_value: str
    description: Optional[str] = None


class AgentConfigResponse(AgentConfigBase):
    """Agent配置响应模型"""
    id: int
    agent_id: int
    is_sensitive: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserAgentConfigCreate(BaseModel):
    """用户Agent配置创建模型"""
    agent_id: int
    config_key: str
    config_value: str
    config_type: str = "string"


class UserAgentConfigResponse(BaseModel):
    """用户Agent配置响应模型"""
    id: int
    user_id: int
    agent_id: int
    config_key: str
    config_value: str
    config_type: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
