"""
认证相关API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.data.database import get_db
from backend.data.schemas import UserCreate, UserLogin, Token, UserResponse
from backend.data.models import User
from backend.services.auth_service import AuthService
from backend.dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """用户注册"""
    auth_service = AuthService(db)
    
    try:
        user = auth_service.create_user(user_create)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )


@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """用户登录"""
    auth_service = AuthService(db)
    
    # 验证用户身份
    user = auth_service.authenticate_user(user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    tokens = auth_service.create_tokens(user)
    return tokens


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """用户登出"""
    # 在实际应用中，这里可以将token加入黑名单
    # 目前只是返回成功响应
    return {"message": "登出成功"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    # 这里应该验证refresh token，暂时简化处理
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """刷新访问令牌"""
    auth_service = AuthService(db)
    tokens = auth_service.create_tokens(current_user)
    return tokens
