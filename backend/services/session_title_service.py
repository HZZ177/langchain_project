"""
会话标题自动生成服务
专门用于根据对话内容自动生成会话标题的内部服务
"""
import asyncio
import time
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from backend.data.models import Session as SessionModel, Conversation
from backend.services.session_service import SessionService
from backend.services.system_config_service import get_system_config_service
from backend.core.logger import logger


class SessionTitleService:
    """会话标题自动生成服务"""

    def __init__(self, db: Session = None):
        # 初始化基本属性
        self.enabled = False
        self.trigger_rounds = 2
        self.llm = None
        self._current_config = None

        # 如果提供了数据库连接，立即加载配置并初始化
        if db:
            try:
                config = self._load_config_from_db(db)
                self._init_llm(config)
                logger.info(f"SessionTitleService 初始化完成 - 状态: {'启用' if self.enabled else '禁用'}")
            except Exception as e:
                logger.error(f"SessionTitleService 初始化失败: {e}")
                self.enabled = False
    
    def _load_config_from_db(self, db: Session) -> Dict[str, Any]:
        """从数据库加载配置"""
        try:
            config_service = get_system_config_service(db)
            return config_service.get_title_generation_config()
        except Exception as e:
            logger.error(f"从数据库加载标题生成配置失败: {e}")
            # 返回硬编码的默认配置作为最后的后备
            return {
                "enabled": True,
                "model": "gemini-2.5-flash-preview-05-20",
                "api_key": "sk-cvqWUuYL0c6Nw3gK9UH3TtGzfnUWyntiFtolbzw7sgFSWQQ2",
                "base_url": "https://x666.me/v1",
                "temperature": 0.3,
                "max_tokens": None,
                "trigger_rounds": 2
            }

    def _init_llm(self, config: Dict[str, Any]):
        """初始化标题生成专用LLM"""
        # 使用数据库配置
        if not config.get("enabled", True):
            logger.info("会话标题自动生成功能已禁用")
            self.enabled = False
            return

        try:
            # 构建LLM参数，只在max_tokens不为null时添加该参数
            llm_params = {
                "model": config.get("model", "gemini-2.5-flash-preview-05-20"),
                "api_key": config.get("api_key", ""),
                "base_url": config.get("base_url", "https://api.openai.com/v1"),
                "temperature": config.get("temperature", 0.3),
            }
            max_tokens = config.get("max_tokens")
            if max_tokens is not None:
                llm_params["max_tokens"] = max_tokens

            self.llm = ChatOpenAI(**llm_params)
            self.enabled = True
            self.trigger_rounds = config.get("trigger_rounds", 2)
            self._current_config = config
            logger.info(f"标题生成LLM配置更新成功 - 模型: {config.get('model')}")
        except Exception as e:
            logger.error(f"标题生成LLM配置更新失败: {e}")
            self.enabled = False
    
    def should_generate_title(self, session: SessionModel, conversations: List[Conversation], config: Dict[str, Any] = None) -> bool:
        """判断是否应该生成标题"""
        if not self.enabled or not self.llm:
            return False

        # 检查会话标题是否仍为默认值
        if session.name != "新对话":
            return False

        # 获取Agent类型以确定触发条件
        agent_type = session.agent.type if session.agent else "qa_agent"

        # 使用动态配置或默认配置
        base_trigger_rounds = config.get("trigger_rounds", self.trigger_rounds) if config else self.trigger_rounds

        # 根据Agent类型调整触发条件
        if agent_type == "brainstorm_agent":
            # 头脑风暴Agent：用户提供主题后，AI进行内部讨论，1轮即可触发
            trigger_rounds = 1
            logger.info(f"检测到头脑风暴Agent，使用特殊触发条件: {trigger_rounds}轮")
        else:
            # QA Agent等：保持原有逻辑
            trigger_rounds = base_trigger_rounds
            logger.info(f"检测到{agent_type}，使用标准触发条件: {trigger_rounds}轮")

        # 检查对话轮数是否达到触发条件
        user_messages = [conv for conv in conversations if conv.message_type == "user"]
        assistant_messages = [conv for conv in conversations if conv.message_type == "assistant"]

        # 至少需要指定轮数的完整对话（用户+助手）
        min_rounds = min(len(user_messages), len(assistant_messages))

        if min_rounds < trigger_rounds:
            logger.info(f"会话 {session.id} 对话轮数不足 - 当前: {min_rounds}轮, 需要: {trigger_rounds}轮")
            return False

        logger.info(f"会话 {session.id} 满足标题生成条件 - Agent类型: {agent_type}, 对话轮数: {min_rounds}, 触发条件: {trigger_rounds}轮")
        return True
    
    async def generate_title_async(self, session_id: int, db: Session) -> Optional[str]:
        """异步生成会话标题"""
        try:
            # 加载最新配置
            config = self._load_config_from_db(db)

            # 如果配置发生变化，重新初始化LLM
            if config != self._current_config:
                self._init_llm(config)

            if not self.enabled or not self.llm:
                return None

            # 获取会话信息
            session_service = SessionService(db)
            session = session_service.get_session_by_id(session_id)

            if not session:
                logger.warning(f"会话 {session_id} 不存在，跳过标题生成")
                return None

            # 获取对话历史
            conversations = db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).order_by(Conversation.created_at.asc()).limit(10).all()  # 只取前10条对话
            
            # 检查是否需要生成标题
            if not self.should_generate_title(session, conversations, config):
                return None
            
            # 构建对话内容
            conversation_text = self._build_conversation_text(conversations)
            
            # 生成标题
            title = await self._generate_title(conversation_text)
            
            if title:
                # 更新会话标题
                from backend.data.schemas import SessionUpdate
                session_update = SessionUpdate(name=title)
                updated_session = session_service.update_session(session_id, session_update)

                if updated_session:
                    logger.info(f"会话 {session_id} 标题生成成功: '{title}'")

                    # 通过WebSocket通知前端标题更新
                    await self._notify_title_update(session_id, title)

                    return title
                else:
                    logger.error(f"会话 {session_id} 标题更新失败")
            
            return None
            
        except Exception as e:
            logger.error(f"生成会话 {session_id} 标题时发生错误: {e}")
            logger.exception("标题生成异常详情")
            return None
    
    def _build_conversation_text(self, conversations: List[Conversation]) -> str:
        """构建对话文本用于标题生成"""
        lines = []
        for conv in conversations[:6]:  # 只取前3轮对话
            role = "用户" if conv.message_type == "user" else "助手"
            content = conv.content[:200]  # 限制每条消息长度
            lines.append(f"{role}: {content}")
        
        return "\n".join(lines)
    
    async def _generate_title(self, conversation_text: str) -> Optional[str]:
        """使用LLM生成标题"""
        system_prompt = """你是一个专门为AI对话生成简洁标题的助手。

请根据以下对话内容，生成一个简洁、准确的中文标题。

要求：
1. 标题长度控制在5-15个字符
2. 准确概括对话的主要内容或主题
3. 使用简洁、自然的中文表达
4. 不要包含"对话"、"聊天"等词汇
5. 直接输出标题，不要其他内容

示例：
- 对话关于Python编程 → "Python编程问题"
- 对话关于旅行计划 → "旅行计划制定"
- 对话关于健康饮食 → "健康饮食建议"
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"对话内容：\n{conversation_text}")
        ]
        
        try:
            start_time = time.time()
            logger.info("🏷️ 开始生成会话标题...")
            
            response = await self.llm.ainvoke(messages)
            print(response)
            title = response.content.strip()
            
            # 清理标题
            title = self._clean_title(title)
            
            elapsed = time.time() - start_time
            logger.info(f"🏷️ 标题生成完成 - 标题: '{title}', 耗时: {elapsed:.2f}s")
            
            return title
            
        except Exception as e:
            logger.error(f"LLM标题生成失败: {e}")
            return None
    
    def _clean_title(self, title: str) -> str:
        """清理和验证生成的标题"""
        if not title:
            return "新对话"
        
        # 移除引号和多余空格
        title = title.strip().strip('"').strip("'").strip()
        
        # 限制长度
        if len(title) > 20:
            title = title[:20]
        
        # 如果标题太短或包含无效内容，使用默认值
        if len(title) < 2 or title.lower() in ["无", "无标题", "标题", "对话"]:
            return "新对话"
        
        return title

    async def _notify_title_update(self, session_id: int, new_title: str):
        """通过WebSocket通知前端标题更新"""
        try:
            from backend.websocket.manager import websocket_manager

            # 发送标题更新消息到对应会话
            await websocket_manager.send_message(str(session_id), {
                "type": "session_title_updated",
                "data": {
                    "session_id": session_id,
                    "new_title": new_title,
                    "timestamp": time.time()
                }
            })

            logger.info(f"已通知前端会话 {session_id} 标题更新: '{new_title}'")

        except Exception as e:
            logger.error(f"通知前端标题更新失败: {e}")


# 全局标题生成服务实例
title_service = None


def get_title_service(db: Session = None) -> SessionTitleService:
    """获取标题生成服务实例"""
    global title_service

    # 如果还没有实例，或者提供了数据库连接需要重新初始化
    if title_service is None:
        title_service = SessionTitleService(db)
    elif db is not None and not title_service.enabled:
        # 如果服务未启用但提供了数据库连接，尝试重新初始化
        try:
            config = title_service._load_config_from_db(db)
            title_service._init_llm(config)
        except Exception as e:
            logger.error(f"重新初始化标题生成服务失败: {e}")

    return title_service
