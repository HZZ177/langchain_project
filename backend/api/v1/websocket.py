"""
WebSocket相关API
"""
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from backend.data.database import get_db
from backend.core.security import extract_user_from_token
from backend.websocket.manager import websocket_manager
from backend.websocket.router import create_message_router
from backend.core.logger import logger

router = APIRouter()

# 创建消息路由器
message_router = create_message_router(websocket_manager)


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """WebSocket连接端点"""
    
    # 验证token
    user_info = extract_user_from_token(token)
    if not user_info:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    user_id = str(user_info["user_id"])
    
    # 建立WebSocket连接
    await websocket_manager.connect(websocket, session_id, user_id)
    
    try:
        # 发送连接成功消息
        await websocket_manager.send_message(session_id, {
            "type": "connection_established",
            "data": {
                "session_id": session_id,
                "user_id": user_id,
                "message": "WebSocket连接已建立"
            }
        })
        
        # 消息循环
        while True:
            # 接收消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_websocket_message(session_id, message, db)
            except json.JSONDecodeError:
                await websocket_manager.send_message(session_id, {
                    "type": "error",
                    "data": {
                        "code": "INVALID_JSON",
                        "message": "消息格式无效"
                    }
                })
            except Exception as e:
                await websocket_manager.send_message(session_id, {
                    "type": "error",
                    "data": {
                        "code": "MESSAGE_PROCESSING_ERROR",
                        "message": f"处理消息时发生错误: {str(e)}"
                    }
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket连接断开: session_id={session_id}")
    except Exception as e:
        logger.error(f"WebSocket连接异常: session_id={session_id}, error={e}")
    finally:
        # 清理连接
        websocket_manager.disconnect(session_id)


async def handle_websocket_message(session_id: str, message: dict, db: Session):
    """处理WebSocket消息"""
    message_type = message.get("type")
    
    if message_type == "user_message":
        # 处理用户消息
        await message_router.route_message(session_id, message, db)
    
    elif message_type == "ping":
        # 处理ping消息
        await message_router.handle_ping(session_id)
    
    elif message_type == "get_session_info":
        # 处理会话信息请求
        await message_router.handle_session_info(session_id, db)
    
    else:
        # 未知消息类型
        await websocket_manager.send_message(session_id, {
            "type": "error",
            "data": {
                "code": "UNKNOWN_MESSAGE_TYPE",
                "message": f"未知的消息类型: {message_type}"
            }
        })


@router.get("/active-connections")
async def get_active_connections():
    """获取活跃连接信息（调试用）"""
    active_sessions = websocket_manager.get_active_sessions()
    return {
        "total_connections": len(active_sessions),
        "sessions": active_sessions
    }
