"""
问答Agent实现
"""
from typing import AsyncIterator, Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from .base_agent import BaseAgent, AgentMessage, AgentResponse
from backend.core.llm_pool import llm_pool, LLMConnection
from backend.core.logger import logger


class QAAgent(BaseAgent):
    """
    大模型问答Agent
    提供通用的AI问答功能，支持多种问题类型
    """

    def __init__(self, config: Dict[str, Any], agent_id: str = None):
        super().__init__(config)
        self.agent_id = agent_id
        self.config_dict = config
        self.current_connection: Optional[LLMConnection] = None
        logger.info(f"QAAgent初始化 - agent_id: {agent_id}")
    
    def _get_llm_connection(self) -> LLMConnection:
        """从连接池获取LLM连接"""
        if not self.agent_id:
            raise ValueError("Agent ID不能为空")

        # 验证必要的配置
        if not self.config.api_key:
            raise ValueError("API密钥不能为空")

        if not self.config.model_name:
            raise ValueError("模型名称不能为空")

        # 从连接池获取连接
        connection = llm_pool.get_llm_connection(
            agent_id=self.agent_id,
            agent_type="qa_agent",
            config=self.config_dict
        )

        if not connection:
            raise RuntimeError(f"无法从连接池获取LLM连接 - agent_id: {self.agent_id}")

        self.current_connection = connection
        logger.info(f"获取LLM连接成功 - connection_id: {connection.connection_id}")
        return connection

    def _release_llm_connection(self):
        """释放LLM连接回连接池"""
        if self.current_connection:
            llm_pool.release_llm_connection(self.current_connection.connection_id)
            logger.info(f"释放LLM连接 - connection_id: {self.current_connection.connection_id}")
            self.current_connection = None
    
    async def process_message(
        self,
        message: AgentMessage,
        context: Dict[str, Any]
    ) -> AsyncIterator[AgentResponse]:
        """
        处理用户消息并返回流式响应
        """
        connection = None
        try:
            # 从连接池获取LLM连接
            connection = self._get_llm_connection()
            llm = connection.llm

            # 构建消息历史
            messages = self._build_messages(message, context)

            logger.info(f"开始处理消息 - connection_id: {connection.connection_id}, "
                       f"agent_id: {self.agent_id}, message_length: {len(message.content)}")

            # 流式调用LLM
            import time
            start_time = time.time()
            full_response = ""
            chunk_count = 0

            logger.info(f"🤖 开始调用LLM - 模型: {self.config.model_name}, "
                       f"agent_id: {self.agent_id}, connection_id: {connection.connection_id}")

            async for chunk in llm.astream(messages):
                if chunk.content:
                    chunk_count += 1
                    full_response += chunk.content

                    # 每20个chunk记录一次进度
                    if chunk_count % 20 == 0:
                        elapsed = time.time() - start_time
                        logger.info(f"📝 LLM响应进度 - chunk数: {chunk_count}, "
                                   f"累计长度: {len(full_response)}, 耗时: {elapsed:.2f}s")

                    yield AgentResponse(
                        content=chunk.content,
                        is_final=False,
                        metadata={
                            "model": self.config.model_name,
                            "temperature": self.config.temperature,
                            "connection_id": connection.connection_id
                        }
                    )

            # 记录完成信息
            total_time = time.time() - start_time
            logger.info(f"✅ LLM响应完成 - 模型: {self.config.model_name}, "
                       f"总chunk数: {chunk_count}, 总长度: {len(full_response)}, "
                       f"总耗时: {total_time:.2f}s, 平均速度: {len(full_response)/total_time:.1f}字符/秒")

            # 发送最终响应标记
            yield AgentResponse(
                content="",
                is_final=True,
                metadata={
                    "model": self.config.model_name,
                    "total_tokens": len(full_response.split()),
                    "full_response": full_response,
                    "connection_id": connection.connection_id,
                    "usage_count": connection.usage_count,
                    "total_time": total_time,
                    "chunk_count": chunk_count
                }
            )

            logger.info(f"消息处理完成 - connection_id: {connection.connection_id}, "
                       f"response_length: {len(full_response)}")

        except Exception as e:
            logger.error(f"处理消息失败 - agent_id: {self.agent_id}, 错误: {e}")
            yield AgentResponse(
                content=f"抱歉，处理您的请求时发生错误: {str(e)}",
                is_final=True,
                metadata={"error": str(e)}
            )
        finally:
            # 确保释放连接
            if connection:
                self._release_llm_connection()
    
    def _build_messages(self, message: AgentMessage, context: Dict[str, Any]) -> List:
        """构建LangChain消息列表"""
        messages = []
        
        # 添加系统消息
        system_prompt = "你是一个有用的AI助手，能够进行自然的中文对话。请提供准确、有帮助的回答。"
        messages.append(SystemMessage(content=system_prompt))
        
        # 添加历史对话
        conversations = context.get("conversations", [])
        max_rounds = getattr(self.config, 'max_conversation_rounds', 5)  # 从配置获取轮数，默认5轮
        for conv in conversations[-max_rounds:]:  # 保留最近N轮对话
            if conv["message_type"] == "user":
                messages.append(HumanMessage(content=conv["content"]))
            elif conv["message_type"] == "assistant":
                messages.append(AIMessage(content=conv["content"]))
        
        # 添加当前用户消息
        messages.append(HumanMessage(content=message.content))
        
        return messages
    
    def get_config_schema(self) -> Dict[str, Any]:
        """返回配置模式定义"""
        return {
            "type": "object",
            "properties": {
                "model_name": {
                    "type": "string",
                    "default": "gemini-2.5-flash-preview-05-20",
                    "description": "使用的模型名称"
                },
                "temperature": {
                    "type": "number",
                    "default": 0.7,
                    "minimum": 0.0,
                    "maximum": 2.0,
                    "description": "控制回答的随机性"
                },
                "max_tokens": {
                    "type": ["integer", "null"],
                    "default": None,
                    "minimum": 1,
                    "description": "最大生成token数，留空表示无限制"
                },
                "api_key": {
                    "type": "string",
                    "description": "OpenAI API密钥"
                },
                "base_url": {
                    "type": "string",
                    "default": "https://api.openai.com/v1",
                    "description": "API基础URL"
                }
            },
            "required": ["model_name", "api_key"]
        }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置参数"""
        required_fields = ["model_name", "api_key"]
        
        # 检查必需字段
        for field in required_fields:
            if field not in config or not config[field]:
                return False
        
        # 检查temperature范围
        if "temperature" in config:
            temp = config["temperature"]
            if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                return False
        
        # 检查max_tokens范围
        if "max_tokens" in config:
            max_tokens = config["max_tokens"]
            if max_tokens is not None:
                if not isinstance(max_tokens, int) or max_tokens < 1:
                    return False
        
        return True
    
    def get_supported_features(self) -> List[str]:
        """返回支持的功能特性"""
        return [
            "basic_chat",
            "streaming_response",
            "conversation_history",
            "configurable_model"
        ]
