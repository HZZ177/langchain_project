"""
问答Agent实现
"""
from typing import AsyncIterator, Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from .base_agent import BaseAgent, AgentMessage, AgentResponse


class QAAgent(BaseAgent):
    """
    大模型问答Agent
    提供通用的AI问答功能，支持多种问题类型
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.llm = self._create_llm()
    
    def _create_llm(self) -> ChatOpenAI:
        """创建LangChain LLM实例"""
        # 验证必要的配置
        if not self.config.api_key:
            raise ValueError("API密钥不能为空")

        if not self.config.model_name:
            raise ValueError("模型名称不能为空")

        print(f"创建LLM实例: model={self.config.model_name}, temperature={self.config.temperature}, max_tokens={self.config.max_tokens}, base_url={self.config.base_url}")

        return ChatOpenAI(
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            streaming=True
        )
    
    async def process_message(
        self, 
        message: AgentMessage, 
        context: Dict[str, Any]
    ) -> AsyncIterator[AgentResponse]:
        """
        处理用户消息并返回流式响应
        """
        try:
            # 构建消息历史
            messages = self._build_messages(message, context)
            
            # 流式调用LLM
            full_response = ""
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    full_response += chunk.content
                    yield AgentResponse(
                        content=chunk.content,
                        is_final=False,
                        metadata={
                            "model": self.config.model_name,
                            "temperature": self.config.temperature
                        }
                    )
            
            # 发送最终响应标记
            yield AgentResponse(
                content="",
                is_final=True,
                metadata={
                    "model": self.config.model_name,
                    "total_tokens": len(full_response.split()),
                    "full_response": full_response
                }
            )
            
        except Exception as e:
            yield AgentResponse(
                content=f"抱歉，处理您的请求时发生错误: {str(e)}",
                is_final=True,
                metadata={"error": str(e)}
            )
    
    def _build_messages(self, message: AgentMessage, context: Dict[str, Any]) -> List:
        """构建LangChain消息列表"""
        messages = []
        
        # 添加系统消息
        system_prompt = "你是一个有用的AI助手，能够进行自然的中文对话。请提供准确、有帮助的回答。"
        messages.append(SystemMessage(content=system_prompt))
        
        # 添加历史对话
        conversations = context.get("conversations", [])
        for conv in conversations[-10:]:  # 只保留最近10轮对话
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
                    "default": "gpt-3.5-turbo",
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
