"""
会话和对话服务
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.data.models import Session as SessionModel, Conversation
from backend.data.schemas import SessionCreate, SessionUpdate, ConversationCreate


class SessionService:
    """会话服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_sessions(self, user_id: int) -> List[SessionModel]:
        """获取用户的会话列表"""
        return self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.is_active == True
        ).order_by(SessionModel.updated_at.desc()).all()
    
    def get_session_by_id(self, session_id: int, user_id: Optional[int] = None) -> Optional[SessionModel]:
        """根据ID获取会话"""
        query = self.db.query(SessionModel).filter(SessionModel.id == session_id)
        
        if user_id:
            query = query.filter(SessionModel.user_id == user_id)
        
        return query.first()
    
    def create_session(self, user_id: int, session_create: SessionCreate) -> SessionModel:
        """创建新会话"""
        db_session = SessionModel(
            user_id=user_id,
            agent_id=session_create.agent_id,
            name=session_create.name
        )
        
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        
        return db_session
    
    def update_session(self, session_id: int, session_update: SessionUpdate, 
                      user_id: Optional[int] = None) -> Optional[SessionModel]:
        """更新会话"""
        db_session = self.get_session_by_id(session_id, user_id)
        if not db_session:
            return None
        
        update_data = session_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_session, field, value)
        
        self.db.commit()
        self.db.refresh(db_session)
        
        return db_session
    
    def delete_session(self, session_id: int, user_id: Optional[int] = None) -> bool:
        """删除会话（软删除）"""
        db_session = self.get_session_by_id(session_id, user_id)
        if not db_session:
            return False
        
        db_session.is_active = False
        self.db.commit()
        
        return True


class ConversationService:
    """对话服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_session_conversations(self, session_id: int, limit: int = 100) -> List[Conversation]:
        """获取会话的对话历史"""
        return self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).order_by(Conversation.created_at.asc()).limit(limit).all()
    
    def create_conversation(self, conversation_create: ConversationCreate) -> Conversation:
        """创建对话记录"""
        db_conversation = Conversation(
            session_id=conversation_create.session_id,
            message_type=conversation_create.message_type,
            content=conversation_create.content,
            extra_data=conversation_create.extra_data
        )
        
        self.db.add(db_conversation)
        self.db.commit()
        self.db.refresh(db_conversation)
        
        return db_conversation
    
    def clear_session_conversations(self, session_id: int) -> bool:
        """清空会话的对话历史"""
        try:
            self.db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).delete()
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
