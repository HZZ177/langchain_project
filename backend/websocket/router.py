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
from backend.services.session_title_service import get_title_service
from backend.data.schemas import ConversationCreate
from backend.core.logger import logger
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
            agent_config = agent_service.get_agent_config(session_info.agent_id)

            logger.debug(f"获取到的Agent配置: {agent_config}")

            if not agent_config:
                await self._send_error(session_id, "AGENT_CONFIG_NOT_FOUND", "Agent配置不存在")
                return
            
            # 4. 获取Agent实例
            agent_info = agent_service.get_agent_by_id(session_info.agent_id)
            if not agent_info:
                await self._send_error(session_id, "AGENT_NOT_FOUND", "Agent不存在")
                return

            logger.info(f"开始获取Agent实例 - session_id: {session_id}, agent_id: {session_info.agent_id}, agent_type: {agent_info.type}")

            agent = agent_manager.get_agent_instance(
                str(session_info.agent_id),
                agent_info.type,
                agent_config
            )

            if not agent:
                await self._send_error(session_id, "AGENT_CREATE_FAILED", "Agent创建失败")
                return

            logger.info(f"Agent实例获取成功 - session_id: {session_id}, agent_id: {session_info.agent_id}")
            
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
                if response.is_final:
                    # 检查是否是头脑风暴Agent
                    if agent.__class__.__name__ == 'BrainstormAgent':
                        # 头脑风暴Agent需要特殊处理
                        if response.metadata and response.metadata.get("discussion_phase") == "complete":
                            # 构建完整的头脑风暴会话数据
                            discussion_history = response.metadata.get("discussion_history", [])

                            # 从讨论历史重建头脑风暴会话结构
                            brainstorm_session = {
                                "topic": validated_message["content"],  # 用户输入的主题
                                "config": {
                                    "model_a": agent.config_dict.get('model_a_name', 'gemini-2.5-flash-preview-05-20'),
                                    "model_b": agent.config_dict.get('model_b_name', 'Claude-3'),
                                    "style": agent.config_dict.get('discussion_style', 'collaborative'),
                                    "max_rounds": agent.config_dict.get('max_discussion_rounds', 5)
                                },
                                "rounds": [],
                                "summary": "",
                                "isComplete": True
                            }

                            # 重建轮次数据
                            current_round = None
                            for item in discussion_history:
                                round_num = item["round"]
                                speaker = item["speaker"]
                                content = item["content"]

                                # 如果是新轮次，创建新的轮次对象
                                if not current_round or current_round["round"] != round_num:
                                    if current_round:
                                        brainstorm_session["rounds"].append(current_round)
                                    current_round = {
                                        "round": round_num,
                                        "modelA": {"content": "", "isStreaming": False, "isComplete": False},
                                        "modelB": {"content": "", "isStreaming": False, "isComplete": False}
                                    }

                                # 填充对应模型的内容
                                if speaker == "model_a":
                                    current_round["modelA"]["content"] = content
                                    current_round["modelA"]["isComplete"] = True
                                elif speaker == "model_b":
                                    current_round["modelB"]["content"] = content
                                    current_round["modelB"]["isComplete"] = True

                            # 添加最后一轮
                            if current_round:
                                brainstorm_session["rounds"].append(current_round)

                            # 从metadata中获取总结内容
                            summary_content = response.metadata.get("summary_content", "")
                            if summary_content:
                                brainstorm_session["summary"] = summary_content.strip()
                                logger.info(f"获取到总结内容，长度: {len(summary_content)}")
                            else:
                                logger.warning("未获取到总结内容")

                            logger.info(f"保存头脑风暴会话数据: {len(brainstorm_session['rounds'])}轮讨论，总结长度: {len(brainstorm_session['summary'])}")

                            # 保存头脑风暴会话数据
                            conversation_service.create_conversation(
                                ConversationCreate(
                                    session_id=session_info.id,
                                    message_type="assistant",
                                    content=json.dumps(brainstorm_session, ensure_ascii=False),
                                    extra_data={"type": "brainstorm_session"}
                                )
                            )
                        else:
                            logger.warning("头脑风暴Agent最终响应缺少完整的讨论数据")
                    else:
                        # 普通Agent的处理逻辑
                        if full_response:
                            conversation_service.create_conversation(
                                ConversationCreate(
                                    session_id=session_info.id,
                                    message_type="assistant",
                                    content=full_response
                                )
                            )

                    # 异步触发会话标题生成（不阻塞当前流程）
                    try:
                        title_service = get_title_service()
                        # 使用asyncio.create_task在后台异步执行
                        import asyncio
                        asyncio.create_task(title_service.generate_title_async(session_info.id, db))
                        logger.debug(f"已触发会话 {session_info.id} 的标题生成任务")
                    except Exception as title_error:
                        logger.error(f"触发标题生成失败: {title_error}")

        except Exception as e:
            logger.error(f"消息路由处理异常: {e}")
            logger.exception("消息路由处理异常详情")
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
