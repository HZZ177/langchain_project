"""
依赖注入
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.data.database import get_db
from backend.data.models import User
from backend.core.security import extract_user_from_token
from backend.services.auth_service import AuthService

# HTTP Bearer认证
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前认证用户"""
    token = credentials.credentials
    
    # 从token中提取用户信息
    user_info = extract_user_from_token(token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从数据库获取用户
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_info["user_id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户账号已被禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前管理员用户"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """获取认证服务"""
    return AuthService(db)


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取可选的当前用户（用于可选认证的接口）"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_info = extract_user_from_token(token)
        if not user_info:
            return None
        
        auth_service = AuthService(db)
        user = auth_service.get_user_by_id(user_info["user_id"])
        
        if not user or not user.is_active:
            return None
        
        return user
    except Exception:
        return None
