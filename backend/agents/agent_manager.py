"""
Agent管理器
"""
from typing import Dict, Type, Optional
from .base_agent import BaseAgent
from .qa_agent import QAAgent


class AgentManager:
    """Agent管理器，负责Agent的创建和管理"""
    
    def __init__(self):
        self._agent_classes: Dict[str, Type[BaseAgent]] = {
            "qa_agent": QAAgent,
        }
        self._agent_instances: Dict[str, BaseAgent] = {}
    
    def get_agent_class(self, agent_type: str) -> Optional[Type[BaseAgent]]:
        """获取Agent类"""
        return self._agent_classes.get(agent_type)
    
    def create_agent(self, agent_type: str, config: Dict[str, any]) -> Optional[BaseAgent]:
        """创建Agent实例"""
        agent_class = self.get_agent_class(agent_type)
        if not agent_class:
            print(f"未找到Agent类型: {agent_type}")
            return None

        # 验证必要的配置项
        if not self._validate_required_config(agent_type, config):
            print(f"Agent配置验证失败: {config}")
            return None

        try:
            agent = agent_class(config)
            print(f"Agent创建成功: {agent_type}")
            return agent
        except Exception as e:
            print(f"创建Agent失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_agent_instance(self, agent_id: str, agent_type: str, config: Dict[str, any]) -> Optional[BaseAgent]:
        """获取Agent实例（带缓存）"""
        cache_key = f"{agent_id}_{agent_type}"
        
        # 检查缓存
        if cache_key in self._agent_instances:
            return self._agent_instances[cache_key]
        
        # 创建新实例
        agent = self.create_agent(agent_type, config)
        if agent:
            self._agent_instances[cache_key] = agent
        
        return agent
    
    def get_available_agent_types(self) -> Dict[str, Dict[str, any]]:
        """获取可用的Agent类型信息"""
        agent_types = {}

        for agent_type, agent_class in self._agent_classes.items():
            # 创建临时实例获取信息（不实际初始化LLM）
            try:
                # 使用最小配置创建临时实例
                temp_config = {
                    "model_name": "gpt-3.5-turbo",
                    "api_key": "temp_key_for_schema_only",
                    "base_url": "https://api.openai.com/v1"
                }

                # 直接调用类方法获取配置模式，避免实际初始化
                if hasattr(agent_class, 'get_config_schema_static'):
                    config_schema = agent_class.get_config_schema_static()
                else:
                    # 如果没有静态方法，创建临时实例但不初始化LLM
                    temp_agent = agent_class.__new__(agent_class)
                    temp_agent.config = temp_agent._parse_config(temp_config)
                    config_schema = temp_agent.get_config_schema()

                agent_types[agent_type] = {
                    "name": agent_class.__name__,
                    "description": agent_class.__doc__ or "",
                    "config_schema": config_schema,
                    "supported_features": ["basic_chat", "streaming_response"]
                }
            except Exception as e:
                print(f"获取Agent类型信息失败 {agent_type}: {e}")
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
            temp_agent = agent_class(config)
            return temp_agent.validate_config(config)
        except Exception:
            return False
    
    def clear_cache(self):
        """清空Agent实例缓存"""
        self._agent_instances.clear()
    
    def remove_agent_from_cache(self, agent_id: str, agent_type: str):
        """从缓存中移除特定Agent实例"""
        cache_key = f"{agent_id}_{agent_type}"
        if cache_key in self._agent_instances:
            del self._agent_instances[cache_key]

    def _validate_required_config(self, agent_type: str, config: Dict[str, any]) -> bool:
        """验证必要的配置项"""
        if agent_type == "qa_agent":
            required_keys = ["api_key", "model_name"]
            for key in required_keys:
                if not config.get(key):
                    print(f"缺少必要配置项: {key}")
                    return False
        return True




# 全局Agent管理器实例
agent_manager = AgentManager()
