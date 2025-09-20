"""
会话相关API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.data.database import get_db
from backend.data.schemas import SessionResponse, SessionCreate, SessionUpdate, ConversationResponse
from backend.data.models import User
from backend.services.session_service import SessionService, ConversationService
from backend.services.agent_service import AgentService
from backend.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=List[SessionResponse])
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户会话列表"""
    session_service = SessionService(db)
    sessions = session_service.get_user_sessions(current_user.id)
    return sessions


@router.post("/", response_model=SessionResponse)
async def create_session(
    session_create: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新会话"""
    # 验证Agent是否存在
    agent_service = AgentService(db)
    agent = agent_service.get_agent_by_id(session_create.agent_id)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent不存在"
        )
    
    session_service = SessionService(db)
    
    try:
        session = session_service.create_session(current_user.id, session_create)
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建会话失败: {str(e)}"
        )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取会话详情"""
    session_service = SessionService(db)
    session = session_service.get_session_by_id(session_id, current_user.id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    return session


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    session_update: SessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新会话信息"""
    session_service = SessionService(db)
    
    updated_session = session_service.update_session(
        session_id, session_update, current_user.id
    )
    
    if not updated_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    return updated_session


@router.delete("/{session_id}")
async def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除会话"""
    session_service = SessionService(db)
    
    success = session_service.delete_session(session_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    return {"message": "会话删除成功"}


@router.get("/{session_id}/conversations", response_model=List[ConversationResponse])
async def get_session_conversations(
    session_id: int,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取会话的对话历史"""
    # 验证会话是否属于当前用户
    session_service = SessionService(db)
    session = session_service.get_session_by_id(session_id, current_user.id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    conversation_service = ConversationService(db)
    conversations = conversation_service.get_session_conversations(session_id, limit)
    
    return conversations


@router.delete("/{session_id}/conversations")
async def clear_session_conversations(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """清空会话的对话历史"""
    # 验证会话是否属于当前用户
    session_service = SessionService(db)
    session = session_service.get_session_by_id(session_id, current_user.id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    conversation_service = ConversationService(db)
    success = conversation_service.clear_session_conversations(session_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="清空对话历史失败"
        )
    
    return {"message": "对话历史清空成功"}
