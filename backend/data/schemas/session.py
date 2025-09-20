"""
会话和对话相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class SessionBase(BaseModel):
    """会话基础模型"""
    name: str = "新对话"


class SessionCreate(SessionBase):
    """会话创建模型"""
    agent_id: int


class SessionUpdate(BaseModel):
    """会话更新模型"""
    name: Optional[str] = None
    is_active: Optional[bool] = None


class SessionResponse(SessionBase):
    """会话响应模型"""
    id: int
    user_id: int
    agent_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    """对话基础模型"""
    message_type: str  # 'user', 'assistant', 'system'
    content: str
    extra_data: Optional[Dict[str, Any]] = None


class ConversationCreate(ConversationBase):
    """对话创建模型"""
    session_id: int


class ConversationResponse(ConversationBase):
    """对话响应模型"""
    id: int
    session_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageRequest(BaseModel):
    """消息请求模型"""
    content: str
    session_id: int


class MessageResponse(BaseModel):
    """消息响应模型"""
    content: str
    is_final: bool = False
    extra_data: Optional[Dict[str, Any]] = None
