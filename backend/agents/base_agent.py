"""
Agent基础类和接口定义
"""
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any, Optional, List
from pydantic import BaseModel


class AgentMessage(BaseModel):
    """Agent消息模型"""
    content: str
    message_type: str = "user"  # "user", "assistant", "system"
    metadata: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    """Agent响应模型"""
    content: str
    is_final: bool = False
    metadata: Optional[Dict[str, Any]] = None


class AgentConfig(BaseModel):
    """Agent配置基类"""
    model_config = {"protected_namespaces": ()}

    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None


class BaseAgent(ABC):
    """所有Agent的基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = self._parse_config(config)
        self.agent_type = self.__class__.__name__
    
    def _parse_config(self, config: Dict[str, Any]) -> AgentConfig:
        """解析配置参数"""
        return AgentConfig(**config)
    
    @abstractmethod
    async def process_message(
        self, 
        message: AgentMessage, 
        context: Dict[str, Any]
    ) -> AsyncIterator[AgentResponse]:
        """
        处理用户消息并返回流式响应
        
        Args:
            message: 用户输入消息
            context: 上下文信息（会话历史、用户信息等）
            
        Yields:
            AgentResponse: 流式响应内容
        """
        pass
    
    @abstractmethod
    def get_config_schema(self) -> Dict[str, Any]:
        """
        返回Agent的配置模式定义
        
        Returns:
            Dict: JSON Schema格式的配置定义
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置参数的有效性
        
        Args:
            config: 配置参数字典
            
        Returns:
            bool: 配置是否有效
        """
        pass
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        返回Agent的基本信息
        
        Returns:
            Dict: Agent信息
        """
        return {
            "name": self.agent_type,
            "description": self.__doc__ or "",
            "config_schema": self.get_config_schema(),
            "supported_features": self.get_supported_features()
        }
    
    def get_supported_features(self) -> List[str]:
        """
        返回Agent支持的功能特性
        
        Returns:
            List[str]: 支持的功能列表
        """
        return ["basic_chat"]
    
    def _format_conversation_history(self, conversations: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        格式化对话历史为LangChain格式
        
        Args:
            conversations: 对话历史列表
            
        Returns:
            List[Dict]: 格式化后的对话历史
        """
        formatted_history = []
        
        for conv in conversations:
            if conv["message_type"] == "user":
                formatted_history.append({"role": "user", "content": conv["content"]})
            elif conv["message_type"] == "assistant":
                formatted_history.append({"role": "assistant", "content": conv["content"]})
            elif conv["message_type"] == "system":
                formatted_history.append({"role": "system", "content": conv["content"]})
        
        return formatted_history
