"""
认证服务
"""
from typing import Optional
from sqlalchemy.orm import Session
from backend.data.models import User
from backend.data.schemas import UserCreate, UserLogin, Token
from backend.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token


class AuthService:
    """认证服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """验证用户身份"""
        user = self.db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
            
        return user
    
    def create_user(self, user_create: UserCreate) -> User:
        """创建新用户"""
        # 检查用户名是否已存在
        existing_user = self.db.query(User).filter(
            (User.username == user_create.username) | (User.email == user_create.email)
        ).first()
        
        if existing_user:
            raise ValueError("用户名或邮箱已存在")
        
        # 创建新用户
        hashed_password = get_password_hash(user_create.password)
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            password_hash=hashed_password
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def create_tokens(self, user: User) -> Token:
        """创建访问令牌和刷新令牌"""
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.db.query(User).filter(User.username == username).first()
    
    def create_admin_user(self, username: str, email: str, password: str) -> User:
        """创建管理员用户"""
        # 检查是否已存在管理员
        existing_admin = self.db.query(User).filter(User.is_admin == True).first()
        if existing_admin:
            return existing_admin
        
        # 检查用户名和邮箱是否已存在
        existing_user = self.db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            # 如果用户已存在，将其设为管理员
            existing_user.is_admin = True
            self.db.commit()
            return existing_user
        
        # 创建新的管理员用户
        hashed_password = get_password_hash(password)
        admin_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            is_admin=True
        )
        
        self.db.add(admin_user)
        self.db.commit()
        self.db.refresh(admin_user)
        
        return admin_user
