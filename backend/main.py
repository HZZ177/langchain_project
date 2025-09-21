"""
FastAPI应用主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.config import get_settings
from backend.data.database import create_tables, get_db, recreate_tables
from backend.data.models import Agent, AgentConfig
from backend.services.auth_service import AuthService
from backend.services.agent_service import AgentService
from backend.agents.agent_manager import agent_manager
from backend.api.v1 import auth, agents, sessions, websocket, pool
from backend.core.logger import logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("正在启动AI Agent平台...")

    # 创建数据库表（如果遇到问题则重建）
    try:
        create_tables()
        logger.info("数据库表创建完成")
    except Exception as e:
        logger.error(f"数据库表创建失败，尝试重建: {e}")
        recreate_tables()
    
    # 创建管理员账号
    await create_admin_user()
    
    # 创建默认Agent
    await create_default_agents()

    # 预热Agent连接池
    await prewarm_agent_pools()

    logger.info("AI Agent平台启动完成")

    yield

    # 关闭时执行
    logger.info("AI Agent平台正在关闭...")


async def create_admin_user():
    """创建管理员用户"""
    db = next(get_db())
    try:
        auth_service = AuthService(db)
        admin_user = auth_service.create_admin_user(
            username=settings.admin_username,
            email=settings.admin_email,
            password=settings.admin_password
        )
        logger.info(f"管理员账号创建/验证完成: {admin_user.username}")
    except Exception as e:
        logger.error(f"创建管理员账号失败: {e}")
        logger.warning("尝试重建数据库表...")
        db.close()
        recreate_tables()
        # 重新尝试创建管理员
        db = next(get_db())
        try:
            auth_service = AuthService(db)
            admin_user = auth_service.create_admin_user(
                username=settings.admin_username,
                email=settings.admin_email,
                password=settings.admin_password
            )
            logger.info(f"管理员账号创建成功: {admin_user.username}")
        except Exception as retry_e:
            logger.error(f"重试后仍然失败: {retry_e}")
    finally:
        db.close()


async def prewarm_agent_pools():
    """预热Agent连接池"""
    logger.info("开始预热Agent连接池...")

    db = next(get_db())
    try:
        # 获取所有活跃的Agent
        agents = db.query(Agent).filter(Agent.is_active == True).all()

        # 构建Agent配置字典
        agents_config = {}
        agent_service = AgentService(db)

        for agent in agents:
            config = agent_service.get_agent_config(agent.id)
            if config:
                agents_config[str(agent.id)] = {
                    "type": agent.type,
                    "config": config
                }
                logger.info(f"准备预热Agent - id: {agent.id}, name: {agent.name}, type: {agent.type}")

        # 预热连接池
        if agents_config:
            agent_manager.prewarm_agent_pools(agents_config)
            logger.info(f"连接池预热完成 - 预热了 {len(agents_config)} 个Agent")
        else:
            logger.warning("没有找到需要预热的Agent")

    except Exception as e:
        logger.error(f"预热Agent连接池失败: {e}")
        logger.exception("预热Agent连接池异常详情")
    finally:
        db.close()


async def create_default_agents():
    """创建默认Agent"""
    db = next(get_db())
    try:
        # 检查是否已存在QA Agent
        existing_qa_agent = db.query(Agent).filter(
            Agent.type == "qa_agent",
            Agent.is_system == True
        ).first()
        
        if not existing_qa_agent:
            # 创建QA Agent
            qa_agent = Agent(
                name="智能问答助手",
                type="qa_agent",
                description="通用AI问答功能，支持多种问题类型，提供智能回答和建议",
                is_system=True,
                is_active=True
            )
            db.add(qa_agent)
            db.commit()
            db.refresh(qa_agent)
            
            # 创建Agent配置
            agent_config = AgentConfig(
                agent_id=qa_agent.id,
                model_name=settings.default_model_name,
                temperature=settings.default_temperature,
                max_tokens=settings.default_max_tokens,
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                system_prompt="你是一个有用的AI助手，能够进行自然的中文对话。请提供准确、有帮助的回答。",
                max_conversation_rounds=5
            )
            db.add(agent_config)
            
            db.commit()
            logger.info(f"默认QA Agent创建完成: {qa_agent.name}")
        else:
            logger.info(f"QA Agent已存在: {existing_qa_agent.name}")

    except Exception as e:
        logger.error(f"创建默认Agent失败: {e}")
        db.rollback()
        logger.warning("尝试重建数据库表...")
        db.close()
        recreate_tables()
        # 重新尝试创建Agent
        db = next(get_db())
        try:
            # 重新创建QA Agent
            qa_agent = Agent(
                name="智能问答助手",
                type="qa_agent",
                description="通用AI问答功能，支持多种问题类型，提供智能回答和建议",
                is_system=True,
                is_active=True
            )
            db.add(qa_agent)
            db.commit()
            db.refresh(qa_agent)

            # 创建Agent配置
            agent_config = AgentConfig(
                agent_id=qa_agent.id,
                model_name=settings.default_model_name,
                temperature=settings.default_temperature,
                max_tokens=settings.default_max_tokens,
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                system_prompt="你是一个有用的AI助手，能够进行自然的中文对话。请提供准确、有帮助的回答。",
                max_conversation_rounds=5
            )
            db.add(agent_config)
            db.commit()

            logger.info(f"默认QA Agent创建成功: {qa_agent.name}")
        except Exception as retry_e:
            logger.error(f"重试后仍然失败: {retry_e}")
            db.rollback()
    finally:
        db.close()


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Agent基座平台 - 企业级AI应用平台",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agent管理"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["会话管理"])
app.include_router(websocket.router, prefix="/api/v1", tags=["WebSocket"])
app.include_router(pool.router, prefix="/api/v1/pool", tags=["连接池监控"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用AI Agent基座平台",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "message": "AI Agent平台运行正常"
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("启动服务")
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
