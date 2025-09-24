"""
Agent管理器
"""
from typing import Dict, Type, Optional, Any
from .base_agent import BaseAgent
from .qa_agent import QAAgent
from .brainstorm_agent import BrainstormAgent
from backend.core.llm_pool import llm_pool
from backend.core.logger import logger


class AgentManager:
    """Agent管理器，负责Agent的创建和管理"""
    
    def __init__(self):
        self._agent_classes: Dict[str, Type[BaseAgent]] = {
            "qa_agent": QAAgent,
            "brainstorm_agent": BrainstormAgent,
        }
        self._agent_instances: Dict[str, BaseAgent] = {}
    
    def get_agent_class(self, agent_type: str) -> Optional[Type[BaseAgent]]:
        """获取Agent类"""
        return self._agent_classes.get(agent_type)
    
    def create_agent(self, agent_type: str, config: Dict[str, any], agent_id: str = None) -> Optional[BaseAgent]:
        """创建Agent实例"""
        agent_class = self.get_agent_class(agent_type)
        if not agent_class:
            logger.error(f"未找到Agent类型: {agent_type}")
            return None

        # 验证必要的配置项
        if not self._validate_required_config(agent_type, config):
            logger.error(f"Agent配置验证失败: {config}")
            return None

        try:
            # 传递agent_id给Agent构造函数
            if agent_type in ["qa_agent", "brainstorm_agent"]:
                agent = agent_class(config, agent_id)
            else:
                agent = agent_class(config)

            logger.info(f"Agent创建成功 - agent_type: {agent_type}, agent_id: {agent_id}")
            return agent
        except Exception as e:
            logger.error(f"创建Agent失败 - agent_type: {agent_type}, agent_id: {agent_id}, 错误: {e}")
            return None
    
    def get_agent_instance(self, agent_id: str, agent_type: str, config: Dict[str, any]) -> Optional[BaseAgent]:
        """获取Agent实例（不再使用缓存，每次创建新实例以使用连接池）"""
        # 不再使用Agent实例缓存，因为连接池已经处理了LLM实例的复用
        # 每次创建新的Agent实例，但LLM连接会从连接池复用
        logger.info(f"创建Agent实例 - agent_id: {agent_id}, agent_type: {agent_type}")
        return self.create_agent(agent_type, config, agent_id)
    
    def get_available_agent_types(self) -> Dict[str, Dict[str, any]]:
        """获取可用的Agent类型信息"""
        agent_types = {}

        for agent_type, agent_class in self._agent_classes.items():
            # 创建临时实例获取信息（不实际初始化LLM）
            try:
                # 根据Agent类型使用不同的临时配置
                if agent_type == "brainstorm_agent":
                    temp_config = {
                        "model_a_name": "gemini-2.5-flash-preview-05-20",
                        "model_a_api_key": "temp_key_for_schema_only",
                        "model_b_name": "claude-3-sonnet",
                        "model_b_api_key": "temp_key_for_schema_only"
                    }
                else:
                    temp_config = {
                        "model_name": "gemini-2.5-flash-preview-05-20",
                        "api_key": "temp_key_for_schema_only",
                        "base_url": "https://api.openai.com/v1"
                    }

                # 直接调用类方法获取配置模式，避免实际初始化
                if hasattr(agent_class, 'get_config_schema_static'):
                    config_schema = agent_class.get_config_schema_static()
                else:
                    # 如果没有静态方法，创建临时实例但不初始化LLM
                    temp_agent = agent_class.__new__(agent_class)
                    if hasattr(temp_agent, '_parse_config'):
                        temp_agent.config = temp_agent._parse_config(temp_config)
                    config_schema = temp_agent.get_config_schema()

                    # 获取支持的功能特性
                    if hasattr(temp_agent, 'get_supported_features'):
                        supported_features = temp_agent.get_supported_features()
                    else:
                        supported_features = ["basic_chat", "streaming_response"]

                agent_types[agent_type] = {
                    "name": agent_class.__name__,
                    "description": agent_class.__doc__ or "",
                    "config_schema": config_schema,
                    "supported_features": supported_features
                }
            except Exception as e:
                logger.error(f"获取Agent类型信息失败 {agent_type}: {e}")
                agent_types[agent_type] = {
                    "name": agent_class.__name__,
                    "description": agent_class.__doc__ or "",
                    "config_schema": {},
                    "supported_features": []
                }

        return agent_types
    
    def validate_agent_config(self, agent_type: str, config: Dict[str, any]) -> bool:
        """验证Agent配置"""
        agent_class = self.get_agent_class(agent_type)
        if not agent_class:
            return False

        try:
            # 创建临时Agent实例进行验证（不传agent_id）
            if agent_type in ["qa_agent", "brainstorm_agent"]:
                temp_agent = agent_class(config, "temp_validation")
            else:
                temp_agent = agent_class(config)
            return temp_agent.validate_config(config)
        except Exception:
            return False
    
    def prewarm_agent_pools(self, agents_config: Dict[str, Dict[str, Any]]):
        """预热所有Agent的连接池"""
        logger.info("开始预热Agent连接池...")

        for agent_id, agent_info in agents_config.items():
            agent_type = agent_info.get("type")
            config = agent_info.get("config", {})

            if agent_type and config:
                try:
                    llm_pool.prewarm_agent_pool(agent_id, agent_type, config)
                    logger.info(f"Agent连接池预热成功 - agent_id: {agent_id}, agent_type: {agent_type}")
                except Exception as e:
                    logger.error(f"Agent连接池预热失败 - agent_id: {agent_id}, 错误: {e}")

        logger.info("Agent连接池预热完成")

    def get_pool_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        return llm_pool.get_pool_stats()

    def remove_agent_from_cache(self, agent_id: str, agent_type: str):
        """从缓存中移除特定Agent实例"""
        # 调用新的连接池清理方法
        self.clear_agent_connections(agent_id, agent_type)

    def clear_agent_connections(self, agent_id: str, agent_type: str):
        """清理Agent的连接池和缓存（用于配置更新）"""
        logger.info(f"清理Agent连接 - agent_id: {agent_id}, agent_type: {agent_type}")
        llm_pool.clear_agent_connections(agent_id, agent_type)

    def prewarm_single_agent(self, agent_id: str, agent_type: str, config: Dict[str, Any]):
        """预热单个Agent的连接池"""
        logger.debug(f"预热单个Agent连接池 - agent_id: {agent_id}, agent_type: {agent_type}")
        try:
            llm_pool.prewarm_agent_pool(agent_id, agent_type, config)
            logger.debug(f"单个Agent连接池预热成功 - agent_id: {agent_id}")
        except Exception as e:
            logger.error(f"单个Agent连接池预热失败 - agent_id: {agent_id}, 错误: {e}")
            raise

    def _validate_required_config(self, agent_type: str, config: Dict[str, any]) -> bool:
        """验证必要的配置项"""
        if agent_type == "qa_agent":
            required_keys = ["api_key", "model_name"]
            for key in required_keys:
                if not config.get(key):
                    logger.error(f"缺少必要配置项: {key}")
                    return False
        return True




# 全局Agent管理器实例
agent_manager = AgentManager()
