"""
Agent服务
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.data.models import Agent, AgentDefaultConfig, UserAgentConfig
from backend.data.schemas import AgentCreate, AgentUpdate


class AgentService:
    """Agent服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_agents(self, user_id: Optional[int] = None) -> List[Agent]:
        """获取Agent列表"""
        query = self.db.query(Agent).filter(Agent.is_active == True)
        
        # 如果指定了用户ID，只返回系统Agent和该用户创建的Agent
        if user_id:
            query = query.filter(
                (Agent.is_system == True) | (Agent.created_by == user_id)
            )
        else:
            # 只返回系统Agent
            query = query.filter(Agent.is_system == True)
        
        return query.all()
    
    def get_agent_by_id(self, agent_id: int) -> Optional[Agent]:
        """根据ID获取Agent"""
        return self.db.query(Agent).filter(
            Agent.id == agent_id,
            Agent.is_active == True
        ).first()
    
    def create_agent(self, agent_create: AgentCreate, created_by: Optional[int] = None) -> Agent:
        """创建Agent"""
        db_agent = Agent(
            name=agent_create.name,
            type=agent_create.type,
            description=agent_create.description,
            is_system=agent_create.is_system,
            created_by=created_by
        )
        
        self.db.add(db_agent)
        self.db.commit()
        self.db.refresh(db_agent)
        
        return db_agent
    
    def update_agent(self, agent_id: int, agent_update: AgentUpdate) -> Optional[Agent]:
        """更新Agent"""
        db_agent = self.get_agent_by_id(agent_id)
        if not db_agent:
            return None
        
        update_data = agent_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_agent, field, value)
        
        self.db.commit()
        self.db.refresh(db_agent)
        
        return db_agent
    
    def get_agent_config(self, agent_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        """获取Agent配置（合并默认配置和用户配置）"""
        # 获取默认配置
        default_configs = self.db.query(AgentDefaultConfig).filter(
            AgentDefaultConfig.agent_id == agent_id
        ).all()
        
        config = {}
        for dc in default_configs:
            config[dc.config_key] = self._convert_config_value(dc.config_value, dc.config_type)
        
        # 如果指定了用户ID，获取用户自定义配置并覆盖默认配置
        if user_id:
            user_configs = self.db.query(UserAgentConfig).filter(
                UserAgentConfig.agent_id == agent_id,
                UserAgentConfig.user_id == user_id
            ).all()
            
            for uc in user_configs:
                config[uc.config_key] = self._convert_config_value(uc.config_value, uc.config_type)
        
        return config
    
    def set_user_agent_config(self, user_id: int, agent_id: int, config_key: str, 
                             config_value: str, config_type: str = "string") -> UserAgentConfig:
        """设置用户Agent配置"""
        # 检查是否已存在该配置
        existing_config = self.db.query(UserAgentConfig).filter(
            UserAgentConfig.user_id == user_id,
            UserAgentConfig.agent_id == agent_id,
            UserAgentConfig.config_key == config_key
        ).first()
        
        if existing_config:
            # 更新现有配置
            existing_config.config_value = config_value
            existing_config.config_type = config_type
            self.db.commit()
            self.db.refresh(existing_config)
            return existing_config
        else:
            # 创建新配置
            new_config = UserAgentConfig(
                user_id=user_id,
                agent_id=agent_id,
                config_key=config_key,
                config_value=config_value,
                config_type=config_type
            )
            self.db.add(new_config)
            self.db.commit()
            self.db.refresh(new_config)
            return new_config
    
    def _convert_config_value(self, value: str, config_type: str) -> Any:
        """转换配置值类型"""
        if config_type == "number":
            try:
                return float(value) if '.' in value else int(value)
            except ValueError:
                return value
        elif config_type == "boolean":
            return value.lower() in ("true", "1", "yes", "on")
        elif config_type == "json":
            try:
                import json
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        else:
            return value
