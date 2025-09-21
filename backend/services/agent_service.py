"""
Agent服务
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.data.models import Agent
from backend.data.models.agent import QAAgentConfig, BrainstormAgentConfig
from backend.data.schemas import AgentCreate, AgentUpdate
from backend.data.schemas.agent import (
    QAAgentConfigCreate, QAAgentConfigUpdate,
    BrainstormAgentConfigCreate, BrainstormAgentConfigUpdate
)


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
        """获取Agent配置 - 多态方式"""
        # 首先获取Agent信息以确定类型
        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return {}

        if agent.type == "qa_agent":
            # 查询QA Agent配置
            qa_config = self.db.query(QAAgentConfig).filter(
                QAAgentConfig.agent_id == agent_id
            ).first()

            if not qa_config:
                return {}

            return {
                "model_name": qa_config.model_name,
                "temperature": qa_config.temperature,
                "max_tokens": qa_config.max_tokens,
                "api_key": qa_config.api_key,
                "base_url": qa_config.base_url,
                "system_prompt": qa_config.system_prompt,
                "max_conversation_rounds": qa_config.max_conversation_rounds
            }

        elif agent.type == "brainstorm_agent":
            # 查询Brainstorm Agent配置
            brainstorm_config = self.db.query(BrainstormAgentConfig).filter(
                BrainstormAgentConfig.agent_id == agent_id
            ).first()

            if not brainstorm_config:
                return {}

            return {
                "model_a_name": brainstorm_config.model_a_name,
                "model_a_temperature": brainstorm_config.model_a_temperature,
                "model_a_api_key": brainstorm_config.model_a_api_key,
                "model_a_base_url": brainstorm_config.model_a_base_url,
                "model_a_system_prompt": brainstorm_config.model_a_system_prompt,

                "model_b_name": brainstorm_config.model_b_name,
                "model_b_temperature": brainstorm_config.model_b_temperature,
                "model_b_api_key": brainstorm_config.model_b_api_key,
                "model_b_base_url": brainstorm_config.model_b_base_url,
                "model_b_system_prompt": brainstorm_config.model_b_system_prompt,

                "max_discussion_rounds": brainstorm_config.max_discussion_rounds,
                "discussion_style": brainstorm_config.discussion_style,
                "enable_summary": brainstorm_config.enable_summary,
                "summary_prompt": brainstorm_config.summary_prompt
            }

        return {}

    def update_agent_config(self, agent_id: int, config_data: Dict[str, Any]) -> bool:
        """更新Agent配置 - 多态方式"""
        # 首先获取Agent信息以确定类型
        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return False

        if agent.type == "qa_agent":
            # 更新QA Agent配置
            qa_config = self.db.query(QAAgentConfig).filter(
                QAAgentConfig.agent_id == agent_id
            ).first()

            if not qa_config:
                # 创建新的QA配置（使用数据库字段默认值）
                qa_config = QAAgentConfig(agent_id=agent_id)
                # 只设置用户提供的非空值
                for key, value in config_data.items():
                    if hasattr(qa_config, key) and value is not None:
                        setattr(qa_config, key, value)
                self.db.add(qa_config)
            else:
                # 更新现有配置
                for key, value in config_data.items():
                    if hasattr(qa_config, key) and value is not None:
                        setattr(qa_config, key, value)

        elif agent.type == "brainstorm_agent":
            # 更新Brainstorm Agent配置
            brainstorm_config = self.db.query(BrainstormAgentConfig).filter(
                BrainstormAgentConfig.agent_id == agent_id
            ).first()

            if not brainstorm_config:
                # 创建新的Brainstorm配置（使用数据库字段默认值）
                brainstorm_config = BrainstormAgentConfig(agent_id=agent_id)
                # 只设置用户提供的非空值
                for key, value in config_data.items():
                    if hasattr(brainstorm_config, key) and value is not None:
                        setattr(brainstorm_config, key, value)
                self.db.add(brainstorm_config)
            else:
                # 更新现有配置
                for key, value in config_data.items():
                    if hasattr(brainstorm_config, key) and value is not None:
                        setattr(brainstorm_config, key, value)
        else:
            return False

        self.db.commit()
        return True


