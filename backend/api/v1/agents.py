"""
Agent相关API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.data.database import get_db
from backend.data.schemas import AgentResponse, AgentCreate, AgentUpdate
from backend.data.models import User
from backend.services.agent_service import AgentService
from backend.agents.agent_manager import agent_manager
from backend.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=List[AgentResponse])
async def get_agents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户可访问的Agent列表"""
    agent_service = AgentService(db)
    agents = agent_service.get_agents(current_user.id)
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取Agent详情"""
    agent_service = AgentService(db)
    agent = agent_service.get_agent_by_id(agent_id)
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent不存在"
        )
    
    return agent


@router.post("/", response_model=AgentResponse)
async def create_agent(
    agent_create: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建自定义Agent"""
    agent_service = AgentService(db)
    
    try:
        agent = agent_service.create_agent(agent_create, current_user.id)
        return agent
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建Agent失败: {str(e)}"
        )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新Agent配置"""
    agent_service = AgentService(db)
    
    # 检查Agent是否存在
    agent = agent_service.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent不存在"
        )
    
    # 检查权限（只有创建者或管理员可以修改）
    if not current_user.is_admin and agent.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改此Agent"
        )
    
    updated_agent = agent_service.update_agent(agent_id, agent_update)
    if not updated_agent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新Agent失败"
        )
    
    return updated_agent


@router.get("/{agent_id}/config")
async def get_agent_config(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取Agent配置"""
    agent_service = AgentService(db)
    
    # 检查Agent是否存在
    agent = agent_service.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent不存在"
        )
    
    config = agent_service.get_agent_config(agent_id, current_user.id)
    return {"config": config}


@router.get("/{agent_id}/config-schema")
async def get_agent_config_schema(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取Agent配置模式"""
    agent_service = AgentService(db)
    
    # 检查Agent是否存在
    agent = agent_service.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent不存在"
        )
    
    # 获取Agent类型信息
    agent_types = agent_manager.get_available_agent_types()
    agent_type_info = agent_types.get(agent.type)
    
    if not agent_type_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent类型不存在"
        )
    
    return {
        "schema": agent_type_info.get("config_schema", {}),
        "supported_features": agent_type_info.get("supported_features", [])
    }


@router.put("/{agent_id}/config")
async def update_agent_config(
    agent_id: int,
    config_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户的Agent配置"""
    agent_service = AgentService(db)
    
    # 检查Agent是否存在
    agent = agent_service.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent不存在"
        )
    
    # 验证配置
    if not agent_manager.validate_agent_config(agent.type, config_data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="配置参数无效"
        )
    
    try:
        # 更新用户配置
        for key, value in config_data.items():
            # 根据值类型判断配置类型
            config_type = "string"
            if value is None:
                config_type = "number"  # null值通常用于数字字段
                value = ""  # 存储为空字符串
            elif isinstance(value, bool):
                config_type = "boolean"
            elif isinstance(value, (int, float)):
                config_type = "number"
            elif isinstance(value, (dict, list)):
                config_type = "json"
                value = str(value)  # JSON序列化

            agent_service.set_user_agent_config(
                current_user.id,
                agent_id,
                key,
                str(value) if value is not None else "",
                config_type
            )

        # 清除Agent实例缓存，确保新配置生效
        agent_manager.remove_agent_from_cache(str(agent_id), agent.type)

        return {"message": "配置更新成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新配置失败: {str(e)}"
        )


@router.get("/types/available")
async def get_available_agent_types():
    """获取可用的Agent类型"""
    agent_types = agent_manager.get_available_agent_types()
    return {"agent_types": agent_types}
