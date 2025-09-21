"""
Agent服务
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.data.models import Agent, AgentConfig
from backend.data.schemas import AgentCreate, AgentUpdate, AgentConfigCreate, AgentConfigUpdate


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
    
    def get_agent_config(self, agent_id: int) -> Dict[str, Any]:
        """获取Agent配置"""
        agent_config = self.db.query(AgentConfig).filter(
            AgentConfig.agent_id == agent_id
        ).first()

        if not agent_config:
            return {}

        return {
            "model_name": agent_config.model_name,
            "temperature": agent_config.temperature,
            "max_tokens": agent_config.max_tokens,
            "api_key": agent_config.api_key,
            "base_url": agent_config.base_url,
            "system_prompt": agent_config.system_prompt
        }

    def create_agent_config(self, agent_config_create: AgentConfigCreate) -> AgentConfig:
        """创建Agent配置"""
        db_config = AgentConfig(
            agent_id=agent_config_create.agent_id,
            model_name=agent_config_create.model_name,
            temperature=agent_config_create.temperature,
            max_tokens=agent_config_create.max_tokens,
            api_key=agent_config_create.api_key,
            base_url=agent_config_create.base_url,
            system_prompt=agent_config_create.system_prompt
        )

        self.db.add(db_config)
        self.db.commit()
        self.db.refresh(db_config)

        return db_config

    def update_agent_config(self, agent_id: int, agent_config_update: AgentConfigUpdate) -> Optional[AgentConfig]:
        """更新Agent配置"""
        db_config = self.db.query(AgentConfig).filter(
            AgentConfig.agent_id == agent_id
        ).first()

        if not db_config:
            return None

        update_data = agent_config_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_config, field, value)

        self.db.commit()
        self.db.refresh(db_config)

        return db_config
