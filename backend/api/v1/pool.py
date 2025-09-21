"""
连接池监控API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.data.database import get_db
from backend.agents.agent_manager import agent_manager
from backend.core.llm_pool import llm_pool
from typing import Dict, Any

router = APIRouter()


@router.get("/stats")
async def get_pool_stats():
    """获取连接池统计信息"""
    try:
        stats = agent_manager.get_pool_stats()
        return {
            "success": True,
            "data": stats,
            "message": "连接池统计信息获取成功"
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "POOL_STATS_ERROR",
                "message": f"获取连接池统计信息失败: {str(e)}"
            }
        }


@router.get("/health")
async def get_pool_health():
    """获取连接池健康状态"""
    try:
        stats = llm_pool.get_pool_stats()
        
        # 计算健康指标
        total_connections = stats["stats"]["current_active"] + stats["stats"]["current_idle"]
        active_ratio = stats["stats"]["current_active"] / max(total_connections, 1)
        
        health_status = "healthy"
        if active_ratio > 0.9:
            health_status = "busy"
        elif total_connections == 0:
            health_status = "empty"
        
        return {
            "success": True,
            "data": {
                "status": health_status,
                "total_connections": total_connections,
                "active_connections": stats["stats"]["current_active"],
                "idle_connections": stats["stats"]["current_idle"],
                "active_ratio": round(active_ratio, 2),
                "total_pools": stats["total_pools"],
                "uptime_stats": {
                    "total_created": stats["stats"]["total_created"],
                    "total_reused": stats["stats"]["total_reused"],
                    "total_released": stats["stats"]["total_released"],
                    "total_recycled": stats["stats"]["total_recycled"]
                }
            },
            "message": f"连接池状态: {health_status}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "POOL_HEALTH_ERROR",
                "message": f"获取连接池健康状态失败: {str(e)}"
            }
        }


@router.get("/details")
async def get_pool_details():
    """获取连接池详细信息"""
    try:
        stats = llm_pool.get_pool_stats()
        
        # 格式化详细信息
        pool_details = []
        for agent_id, details in stats["pool_details"].items():
            pool_details.append({
                "agent_id": agent_id,
                "idle_connections": details["idle_connections"],
                "pool_size": details["pool_size"],
                "utilization": round(
                    (details["pool_size"] - details["idle_connections"]) / details["pool_size"], 2
                ) if details["pool_size"] > 0 else 0
            })
        
        return {
            "success": True,
            "data": {
                "pools": pool_details,
                "global_stats": stats["stats"],
                "summary": {
                    "total_pools": len(pool_details),
                    "total_capacity": sum(p["pool_size"] for p in pool_details),
                    "total_idle": sum(p["idle_connections"] for p in pool_details),
                    "average_utilization": round(
                        sum(p["utilization"] for p in pool_details) / max(len(pool_details), 1), 2
                    )
                }
            },
            "message": "连接池详细信息获取成功"
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "POOL_DETAILS_ERROR",
                "message": f"获取连接池详细信息失败: {str(e)}"
            }
        }


@router.post("/prewarm/{agent_id}")
async def prewarm_agent_pool(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """手动预热指定Agent的连接池"""
    try:
        from backend.services.agent_service import AgentService
        from backend.data.models import Agent
        
        # 获取Agent信息
        agent = db.query(Agent).filter(Agent.id == int(agent_id)).first()
        if not agent:
            return {
                "success": False,
                "error": {
                    "code": "AGENT_NOT_FOUND",
                    "message": f"Agent不存在: {agent_id}"
                }
            }
        
        # 获取Agent配置
        agent_service = AgentService(db)
        config = agent_service.get_agent_config(int(agent_id))
        if not config:
            return {
                "success": False,
                "error": {
                    "code": "AGENT_CONFIG_NOT_FOUND",
                    "message": f"Agent配置不存在: {agent_id}"
                }
            }
        
        # 预热连接池
        llm_pool.prewarm_agent_pool(agent_id, agent.type, config)
        
        return {
            "success": True,
            "data": {
                "agent_id": agent_id,
                "agent_type": agent.type,
                "agent_name": agent.name
            },
            "message": f"Agent连接池预热成功: {agent.name}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "PREWARM_ERROR",
                "message": f"预热Agent连接池失败: {str(e)}"
            }
        }


@router.delete("/clear")
async def clear_all_pools():
    """清空所有连接池（谨慎使用）"""
    try:
        # 获取清理前的统计信息
        before_stats = llm_pool.get_pool_stats()
        
        # 关闭并重新初始化连接池
        llm_pool.shutdown()
        
        return {
            "success": True,
            "data": {
                "cleared_pools": before_stats["total_pools"],
                "cleared_connections": before_stats["stats"]["current_active"] + before_stats["stats"]["current_idle"]
            },
            "message": "所有连接池已清空"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "CLEAR_POOLS_ERROR",
                "message": f"清空连接池失败: {str(e)}"
            }
        }
