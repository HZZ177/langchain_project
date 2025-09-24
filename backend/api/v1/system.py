"""
系统配置相关API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel

from backend.data.database import get_db
from backend.dependencies import get_current_user
from backend.data.models import User
from backend.services.system_config_service import get_system_config_service
from backend.core.logger import logger

router = APIRouter()


class TitleGenerationConfigRequest(BaseModel):
    """标题生成配置请求模型"""
    enabled: bool = True
    model: str = "gemini-2.5-flash-preview-05-20"
    api_key: str = "sk-cvqWUuYL0c6Nw3gK9UH3TtGzfnUWyntiFtolbzw7sgFSWQQ2"
    base_url: str = "https://x666.me/v1"
    temperature: float = 0.3
    max_tokens: Optional[int] = None
    trigger_rounds: int = 2


class TitleGenerationConfigResponse(BaseModel):
    """标题生成配置响应模型"""
    enabled: bool
    model: str
    api_key: str
    base_url: str
    temperature: float
    max_tokens: Optional[int]
    trigger_rounds: int


@router.get("/config/title-generation", response_model=TitleGenerationConfigResponse)
async def get_title_generation_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取标题生成配置"""
    # 检查管理员权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    try:
        config_service = get_system_config_service(db)
        config = config_service.get_title_generation_config()
        
        return TitleGenerationConfigResponse(**config)
        
    except Exception as e:
        logger.error(f"获取标题生成配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取配置失败"
        )


@router.put("/config/title-generation")
async def update_title_generation_config(
    config_request: TitleGenerationConfigRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新标题生成配置"""
    # 检查管理员权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    try:
        config_service = get_system_config_service(db)
        config_dict = config_request.dict()
        
        success = config_service.update_title_generation_config(config_dict)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新配置失败"
            )
        
        logger.info(f"用户 {current_user.username} 更新了标题生成配置")
        
        return {"message": "配置更新成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新标题生成配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新配置失败"
        )


@router.get("/config")
async def get_all_system_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有系统配置（管理员专用）"""
    # 检查管理员权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    try:
        config_service = get_system_config_service(db)
        configs = config_service.get_all_configs()
        
        return {"configs": configs}
        
    except Exception as e:
        logger.error(f"获取系统配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取配置失败"
        )


@router.put("/config")
async def update_system_configs(
    configs: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量更新系统配置（管理员专用）"""
    # 检查管理员权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    try:
        config_service = get_system_config_service(db)
        success = config_service.update_configs(configs)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新配置失败"
            )
        
        logger.info(f"用户 {current_user.username} 批量更新了系统配置")
        
        return {"message": "配置更新成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量更新系统配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新配置失败"
        )
