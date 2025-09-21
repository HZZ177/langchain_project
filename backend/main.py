"""
FastAPI应用主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.config import get_settings
from backend.data.database import create_tables, get_db, recreate_tables
from backend.data.models import Agent, AgentDefaultConfig
from backend.services.auth_service import AuthService
from backend.api.v1 import auth, agents, sessions, websocket

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("正在启动AI Agent平台...")
    
    # 创建数据库表（如果遇到问题则重建）
    try:
        create_tables()
        print("数据库表创建完成")
    except Exception as e:
        print(f"数据库表创建失败，尝试重建: {e}")
        recreate_tables()
    
    # 创建管理员账号
    await create_admin_user()
    
    # 创建默认Agent
    await create_default_agents()
    
    print("AI Agent平台启动完成")
    
    yield
    
    # 关闭时执行
    print("AI Agent平台正在关闭...")


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
        print(f"管理员账号创建/验证完成: {admin_user.username}")
    except Exception as e:
        print(f"创建管理员账号失败: {e}")
        print("尝试重建数据库表...")
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
            print(f"管理员账号创建成功: {admin_user.username}")
        except Exception as retry_e:
            print(f"重试后仍然失败: {retry_e}")
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
            
            # 创建默认配置
            default_configs = [
                {
                    "config_key": "model_name",
                    "config_value": settings.default_model_name,
                    "config_type": "string",
                    "description": "使用的模型名称"
                },
                {
                    "config_key": "temperature",
                    "config_value": str(settings.default_temperature),
                    "config_type": "number",
                    "description": "控制回答的随机性"
                },
                {
                    "config_key": "max_tokens",
                    "config_value": str(settings.default_max_tokens) if settings.default_max_tokens is not None else "",
                    "config_type": "number",
                    "description": "最大生成token数，留空表示无限制"
                },
                {
                    "config_key": "api_key",
                    "config_value": settings.openai_api_key,
                    "config_type": "string",
                    "description": "OpenAI API密钥",
                    "is_sensitive": True
                },
                {
                    "config_key": "base_url",
                    "config_value": settings.openai_base_url,
                    "config_type": "string",
                    "description": "API基础URL"
                }
            ]
            
            for config in default_configs:
                agent_config = AgentDefaultConfig(
                    agent_id=qa_agent.id,
                    **config
                )
                db.add(agent_config)
            
            db.commit()
            print(f"默认QA Agent创建完成: {qa_agent.name}")
        else:
            print(f"QA Agent已存在: {existing_qa_agent.name}")
            
    except Exception as e:
        print(f"创建默认Agent失败: {e}")
        db.rollback()
        print("尝试重建数据库表...")
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
            print(f"默认QA Agent创建成功: {qa_agent.name}")
        except Exception as retry_e:
            print(f"重试后仍然失败: {retry_e}")
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
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
