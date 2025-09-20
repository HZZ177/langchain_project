"""
WebSocket消息路由器
"""
import json
from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.agents.agent_manager import agent_manager
from backend.agents.base_agent import AgentMessage
from backend.services.session_service import SessionService, ConversationService
from backend.services.agent_service import AgentService
from backend.data.schemas import ConversationCreate
from .manager import WebSocketManager


class MessageRouter:
    """消息路由器，处理WebSocket消息分发"""
    
    def __init__(self, ws_manager: WebSocketManager):
        self.ws_manager = ws_manager
    
    async def route_message(self, session_id: str, message: dict, db: Session):
        """路由消息到对应的Agent处理器"""
        try:
            # 1. 验证消息格式
            validated_message = self._validate_message(message)
            if not validated_message:
                await self._send_error(session_id, "INVALID_MESSAGE", "消息格式无效")
                return
            
            # 2. 获取会话信息
            session_service = SessionService(db)
            session_info = session_service.get_session_by_id(int(session_id))
            
            if not session_info:
                await self._send_error(session_id, "SESSION_NOT_FOUND", "会话不存在")
                return
            
            # 3. 获取Agent配置
            agent_service = AgentService(db)
            agent_config = agent_service.get_agent_config(
                session_info.agent_id,
                session_info.user_id
            )

            print(f"获取到的Agent配置: {agent_config}")

            if not agent_config:
                await self._send_error(session_id, "AGENT_CONFIG_NOT_FOUND", "Agent配置不存在")
                return
            
            # 4. 获取Agent实例
            agent_info = agent_service.get_agent_by_id(session_info.agent_id)
            if not agent_info:
                await self._send_error(session_id, "AGENT_NOT_FOUND", "Agent不存在")
                return
            
            agent = agent_manager.get_agent_instance(
                str(session_info.agent_id),
                agent_info.type,
                agent_config
            )
            
            if not agent:
                await self._send_error(session_id, "AGENT_CREATE_FAILED", "Agent创建失败")
                return
            
            # 5. 保存用户消息
            conversation_service = ConversationService(db)
            user_conversation = conversation_service.create_conversation(
                ConversationCreate(
                    session_id=session_info.id,
                    message_type="user",
                    content=validated_message["content"]
                )
            )
            
            # 6. 获取对话历史
            conversations = conversation_service.get_session_conversations(session_info.id)
            conversation_history = [
                {
                    "message_type": conv.message_type,
                    "content": conv.content,
                    "metadata": conv.metadata
                }
                for conv in conversations[:-1]  # 排除刚刚添加的用户消息
            ]
            
            # 7. 构建上下文
            context = {
                "session_id": session_info.id,
                "user_id": session_info.user_id,
                "agent_id": session_info.agent_id,
                "conversations": conversation_history
            }
            
            # 8. 处理消息并流式返回响应
            agent_message = AgentMessage(
                content=validated_message["content"],
                message_type="user"
            )
            
            full_response = ""
            async for response in agent.process_message(agent_message, context):
                # 发送流式响应
                await self.ws_manager.send_message(session_id, {
                    "type": "agent_response",
                    "data": response.dict()
                })
                
                # 收集完整响应
                if response.content:
                    full_response += response.content
                
                # 如果是最终响应，保存到数据库
                if response.is_final and full_response:
                    conversation_service.create_conversation(
                        ConversationCreate(
                            session_id=session_info.id,
                            message_type="assistant",
                            content=full_response,
                            metadata=response.metadata
                        )
                    )
                    
        except Exception as e:
            print(f"消息路由处理异常: {e}")
            await self._send_error(session_id, "PROCESSING_ERROR", f"处理消息时发生错误: {str(e)}")
    
    def _validate_message(self, message: dict) -> dict:
        """验证消息格式"""
        if not isinstance(message, dict):
            return None
        
        if message.get("type") != "user_message":
            return None
        
        data = message.get("data", {})
        if not isinstance(data, dict):
            return None
        
        content = data.get("content")
        if not content or not isinstance(content, str):
            return None
        
        return {
            "content": content.strip(),
            "metadata": data.get("metadata", {})
        }
    
    async def _send_error(self, session_id: str, error_code: str, error_message: str):
        """发送错误消息"""
        await self.ws_manager.send_message(session_id, {
            "type": "error",
            "data": {
                "code": error_code,
                "message": error_message
            }
        })
    
    async def handle_ping(self, session_id: str):
        """处理ping消息"""
        await self.ws_manager.send_message(session_id, {
            "type": "pong",
            "data": {}
        })
    
    async def handle_session_info(self, session_id: str, db: Session):
        """处理会话信息请求"""
        try:
            session_service = SessionService(db)
            session_info = session_service.get_session_by_id(int(session_id))
            
            if session_info:
                await self.ws_manager.send_message(session_id, {
                    "type": "session_info",
                    "data": {
                        "session_id": session_info.id,
                        "agent_id": session_info.agent_id,
                        "session_name": session_info.name
                    }
                })
            else:
                await self._send_error(session_id, "SESSION_NOT_FOUND", "会话不存在")
                
        except Exception as e:
            await self._send_error(session_id, "SESSION_INFO_ERROR", f"获取会话信息失败: {str(e)}")


# 创建全局消息路由器实例
def create_message_router(ws_manager: WebSocketManager) -> MessageRouter:
    """创建消息路由器实例"""
    return MessageRouter(ws_manager)
