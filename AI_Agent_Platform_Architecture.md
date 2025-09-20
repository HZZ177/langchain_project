# AI Agent基座平台 - 架构设计文档

## 1. 项目概述

### 1.1 项目定位
AI Agent基座平台是一个企业级AI应用平台，将通用AI能力封装成特定业务场景的智能Agent，通过统一的Web界面为不同业务部门提供专业化的AI服务。

### 1.2 核心价值
- **业务导向**：以业务流程而非技术模型为核心
- **Agent化服务**：每个Agent专注特定业务场景
- **统一体验**：提供一致的AI交互体验，模仿主流AI官网的交互设计
- **可扩展性**：支持自定义Agent和业务扩展
- **灵活配置**：支持每个Agent独立配置大模型参数

### 1.3 技术栈
- **前端**：Vue 3 + TypeScript + Tailwind CSS
- **后端**：FastAPI + Pydantic + SQLite
- **AI框架**：LangChain + LangGraph

## 2. 整体架构

### 2.1 系统架构
```
前端层 (Vue3 + Tailwind) → API层 (FastAPI) → 服务层 → Agent层 → 数据层 (SQLite)
```

### 2.2 分层职责
- **前端层**：用户界面、状态管理、实时通信
- **API层**：HTTP处理、参数验证、路由分发
- **服务层**：业务逻辑、数据转换、权限控制
- **Agent层**：AI处理、Chain组合、工具调用
- **数据层**：数据库操作、缓存管理、文件存储

## 3. 功能预设

### 3.1 核心功能模块

#### 3.1.1 用户管理
- 基础用户注册和登录
- 用户唯一性验证
- 个人设置和偏好配置
- 用户ID区分个人会话和历史记录

#### 3.1.2 Agent管理
- Agent列表和详情展示
- Agent切换和配置
- 自定义Agent创建
- Agent性能监控

#### 3.1.3 对话管理
- 实时聊天界面
- 流式响应展示
- 对话历史管理
- 消息导出功能

#### 3.1.4 会话管理
- 多会话并行处理
- 会话切换和标签
- 会话搜索和分类
- 会话分享功能

### 3.2 预设Agent类型

#### 3.2.1 大模型问答Agent
- 通用AI问答功能
- 支持多种问题类型
- 提供智能回答和建议
- 标准的一对一对话界面

#### 3.2.2 双模型头脑风暴Agent
- 使用两个不同模型进行头脑风暴
- 用户输入初始背景信息
- 两个模型互相讨论的交流展示
- 多轮对话的头脑风暴界面

#### 3.2.3 Agent配置管理
- 每个Agent独立的大模型配置
- 支持base_url、api_key、temperature等参数
- 实时配置更新和生效

## 4. 技术架构

### 4.0 Agent接口标准化

#### 4.0.1 基础Agent接口
所有Agent必须实现统一的接口标准，确保系统的可扩展性和一致性。

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any, Optional
from pydantic import BaseModel

class AgentMessage(BaseModel):
    content: str
    message_type: str = "user"  # "user", "assistant", "system"
    metadata: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    content: str
    is_final: bool = False
    metadata: Optional[Dict[str, Any]] = None

class AgentConfig(BaseModel):
    """Agent配置基类"""
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None

class BaseAgent(ABC):
    """所有Agent的基类"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent_type = self.__class__.__name__

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
```

#### 4.0.2 双模型头脑风暴Agent设计
```python
class BrainstormAgent(BaseAgent):
    """双模型头脑风暴Agent"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.model_a = self._create_model("model_a")
        self.model_b = self._create_model("model_b")
        self.conversation_controller = ConversationController()

    async def process_message(
        self,
        message: AgentMessage,
        context: Dict[str, Any]
    ) -> AsyncIterator[AgentResponse]:
        """
        实现双模型头脑风暴逻辑
        """
        # 1. 初始化讨论主题
        topic = message.content

        # 2. 设置讨论轮次限制
        max_rounds = context.get("max_rounds", 5)

        # 3. 开始模型间对话
        async for response in self.conversation_controller.start_discussion(
            topic=topic,
            model_a=self.model_a,
            model_b=self.model_b,
            max_rounds=max_rounds
        ):
            yield response

    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "model_a_name": {"type": "string", "default": "gpt-4"},
                "model_b_name": {"type": "string", "default": "claude-3"},
                "max_rounds": {"type": "integer", "default": 5, "minimum": 1, "maximum": 10},
                "discussion_style": {"type": "string", "enum": ["collaborative", "debate"], "default": "collaborative"}
            }
        }

class ConversationController:
    """对话控制器，管理双模型交互"""

    async def start_discussion(
        self,
        topic: str,
        model_a: Any,
        model_b: Any,
        max_rounds: int = 5
    ) -> AsyncIterator[AgentResponse]:
        """
        控制两个模型的讨论过程
        """
        current_speaker = "model_a"
        discussion_history = []

        for round_num in range(max_rounds):
            if current_speaker == "model_a":
                response = await self._get_model_response(model_a, topic, discussion_history, "A")
                current_speaker = "model_b"
            else:
                response = await self._get_model_response(model_b, topic, discussion_history, "B")
                current_speaker = "model_a"

            discussion_history.append(response)

            # 返回当前轮次的响应
            yield AgentResponse(
                content=f"**模型{response['speaker']}**: {response['content']}",
                is_final=False,
                metadata={"round": round_num + 1, "speaker": response['speaker']}
            )

            # 检查是否应该结束讨论
            if await self._should_end_discussion(discussion_history):
                break

        # 生成讨论总结
        summary = await self._generate_summary(topic, discussion_history)
        yield AgentResponse(
            content=f"**讨论总结**: {summary}",
            is_final=True,
            metadata={"type": "summary"}
        )
```

### 4.1 前端架构
- **框架**：Vue 3 Composition API + TypeScript
- **样式**：Tailwind CSS（模仿OpenAI等主流AI官网风格）
- **状态管理**：Pinia
- **路由**：Vue Router
- **HTTP客户端**：Axios
- **UI组件**：自定义组件库

### 4.2 后端架构
- **框架**：FastAPI
- **数据验证**：Pydantic
- **数据库**：SQLite（开发）/ PostgreSQL（生产）
- **ORM**：SQLAlchemy
- **认证**：JWT
- **AI集成**：LangChain + LangGraph
- **实时通信**：WebSocket + SSE
- **消息队列**：Redis（可选）
- **缓存**：Redis
- **加密**：cryptography库

### 4.3 数据库设计

#### 4.3.1 核心表结构

**用户相关表：**
- **用户表 (users)**：用户基本信息
  ```sql
  users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
  ```

**Agent相关表：**
- **Agent表 (agents)**：Agent基本信息和状态
  ```sql
  agents (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'qa_agent', 'brainstorm_agent'
    description TEXT,
    is_system BOOLEAN DEFAULT TRUE, -- 系统预设或用户自定义
    is_active BOOLEAN DEFAULT TRUE,
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
  ```

- **用户Agent权限表 (user_agent_permissions)**：控制用户对Agent的访问权限
  ```sql
  user_agent_permissions (
    id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    agent_id BIGINT REFERENCES agents(id),
    permission_level VARCHAR(20) DEFAULT 'read', -- 'read', 'write', 'admin'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, agent_id)
  )
  ```

**配置相关表：**
- **Agent默认配置表 (agent_default_configs)**：系统级Agent配置
  ```sql
  agent_default_configs (
    id BIGINT PRIMARY KEY,
    agent_id BIGINT REFERENCES agents(id),
    config_key VARCHAR(100) NOT NULL,
    config_value TEXT NOT NULL,
    config_type VARCHAR(20) DEFAULT 'string', -- 'string', 'number', 'boolean', 'json'
    description TEXT,
    is_sensitive BOOLEAN DEFAULT FALSE, -- 是否为敏感信息（如API密钥）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent_id, config_key)
  )
  ```

- **用户Agent配置表 (user_agent_configs)**：用户级Agent配置覆盖
  ```sql
  user_agent_configs (
    id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    agent_id BIGINT REFERENCES agents(id),
    config_key VARCHAR(100) NOT NULL,
    config_value TEXT NOT NULL,
    config_type VARCHAR(20) DEFAULT 'string',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, agent_id, config_key)
  )
  ```

**会话和对话表：**
- **会话表 (sessions)**：对话会话管理
  ```sql
  sessions (
    id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    agent_id BIGINT REFERENCES agents(id),
    name VARCHAR(200) DEFAULT '新对话',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
  ```

- **对话表 (conversations)**：消息内容存储
  ```sql
  conversations (
    id BIGINT PRIMARY KEY,
    session_id BIGINT REFERENCES sessions(id),
    message_type VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    metadata JSON, -- 存储额外信息（如模型参数、响应时间等）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
  ```

**安全相关表：**
- **API密钥表 (api_keys)**：加密存储用户的API密钥
  ```sql
  api_keys (
    id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    provider VARCHAR(50) NOT NULL, -- 'openai', 'anthropic', 'custom'
    key_name VARCHAR(100) NOT NULL,
    encrypted_key TEXT NOT NULL, -- 加密存储的API密钥
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, provider, key_name)
  )
  ```

#### 4.3.2 表关系设计
- **用户 ↔ Agent**：多对多关系（通过user_agent_permissions表）
- **用户 → 会话**：一对多关系
- **Agent → 会话**：一对多关系
- **会话 → 对话**：一对多关系
- **Agent → 默认配置**：一对多关系
- **用户+Agent → 用户配置**：一对多关系
- **用户 → API密钥**：一对多关系

#### 4.3.3 配置优先级机制
配置读取优先级：用户自定义配置 > Agent默认配置 > 系统全局配置

### 4.4 实时通信架构

#### 4.4.1 WebSocket连接管理
```python
class WebSocketManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Set[str]] = {}  # user_id -> session_ids

    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        """建立WebSocket连接"""
        await websocket.accept()
        self.active_connections[session_id] = websocket

        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = set()
        self.user_sessions[user_id].add(session_id)

    def disconnect(self, session_id: str, user_id: str):
        """断开WebSocket连接"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]

        if user_id in self.user_sessions:
            self.user_sessions[user_id].discard(session_id)

    async def send_message(self, session_id: str, message: dict):
        """发送消息到特定会话"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)

    async def broadcast_to_user(self, user_id: str, message: dict):
        """广播消息到用户的所有会话"""
        if user_id in self.user_sessions:
            for session_id in self.user_sessions[user_id]:
                await self.send_message(session_id, message)
```

#### 4.4.2 消息路由器
```python
class MessageRouter:
    """消息路由器，处理WebSocket消息分发"""

    def __init__(self, agent_manager: AgentManager, ws_manager: WebSocketManager):
        self.agent_manager = agent_manager
        self.ws_manager = ws_manager

    async def route_message(self, session_id: str, message: dict):
        """路由消息到对应的Agent处理器"""
        try:
            # 1. 验证消息格式
            validated_message = self._validate_message(message)

            # 2. 获取会话信息
            session_info = await self._get_session_info(session_id)

            # 3. 获取对应的Agent
            agent = await self.agent_manager.get_agent(session_info.agent_id)

            # 4. 处理消息并流式返回响应
            async for response in agent.process_message(validated_message, session_info.context):
                await self.ws_manager.send_message(session_id, {
                    "type": "agent_response",
                    "data": response.dict()
                })

        except Exception as e:
            await self.ws_manager.send_message(session_id, {
                "type": "error",
                "data": {"message": str(e)}
            })
```

#### 4.4.3 消息格式标准
```json
// 客户端发送消息格式
{
  "type": "user_message",
  "data": {
    "content": "用户输入的内容",
    "message_type": "user",
    "metadata": {}
  }
}

// 服务端响应消息格式
{
  "type": "agent_response",
  "data": {
    "content": "AI响应内容",
    "is_final": false,
    "metadata": {
      "model": "gpt-4",
      "tokens_used": 150
    }
  }
}

// 错误消息格式
{
  "type": "error",
  "data": {
    "code": "AGENT_ERROR",
    "message": "Agent处理失败",
    "details": "具体错误信息"
  }
}

// 系统消息格式
{
  "type": "system",
  "data": {
    "event": "session_created",
    "message": "会话已创建"
  }
}
```

## 5. API设计

### 5.1 核心接口

#### 5.1.1 用户认证接口
- **POST /api/v1/auth/register**：用户注册
- **POST /api/v1/auth/login**：用户登录
- **POST /api/v1/auth/logout**：用户登出
- **POST /api/v1/auth/refresh**：刷新Token
- **GET /api/v1/auth/me**：获取当前用户信息
- **PUT /api/v1/auth/profile**：更新用户资料
- **POST /api/v1/auth/reset-password**：重置密码

#### 5.1.2 Agent管理接口
- **GET /api/v1/agents**：获取用户可访问的Agent列表
- **GET /api/v1/agents/{id}**：获取Agent详情
- **POST /api/v1/agents**：创建自定义Agent
- **PUT /api/v1/agents/{id}**：更新Agent配置
- **DELETE /api/v1/agents/{id}**：删除Agent
- **GET /api/v1/agents/{id}/status**：获取Agent状态
- **GET /api/v1/agents/{id}/config-schema**：获取Agent配置模式
- **POST /api/v1/agents/{id}/permissions**：设置Agent权限

#### 5.1.3 对话管理接口
- **POST /api/v1/conversations**：发送消息到Agent
- **GET /api/v1/conversations/{session_id}**：获取对话历史
- **DELETE /api/v1/conversations/{session_id}**：清空对话历史
- **POST /api/v1/conversations/{session_id}/export**：导出对话记录
- **WebSocket /api/v1/conversations/ws/{session_id}**：WebSocket实时对话

#### 5.1.4 会话管理接口
- **GET /api/v1/sessions**：获取用户会话列表
- **POST /api/v1/sessions**：创建新会话
- **PUT /api/v1/sessions/{id}**：更新会话信息
- **DELETE /api/v1/sessions/{id}**：删除会话
- **POST /api/v1/sessions/{id}/switch**：切换会话

#### 5.1.5 配置管理接口
- **GET /api/v1/configs/agents/{agent_id}**：获取用户的Agent配置（合并默认配置和用户配置）
- **PUT /api/v1/configs/agents/{agent_id}**：更新用户的Agent配置
- **DELETE /api/v1/configs/agents/{agent_id}/{config_key}**：删除用户的特定配置项
- **GET /api/v1/configs/agents/{agent_id}/default**：获取Agent默认配置
- **GET /api/v1/configs/system**：获取系统配置
- **PUT /api/v1/configs/system**：更新系统配置

#### 5.1.6 API密钥管理接口
- **GET /api/v1/api-keys**：获取用户的API密钥列表（不返回实际密钥）
- **POST /api/v1/api-keys**：添加新的API密钥
- **PUT /api/v1/api-keys/{id}**：更新API密钥
- **DELETE /api/v1/api-keys/{id}**：删除API密钥
- **POST /api/v1/api-keys/{id}/test**：测试API密钥有效性

#### 5.1.7 系统监控接口
- **GET /api/v1/health**：系统健康检查
- **GET /api/v1/metrics**：系统性能指标
- **GET /api/v1/logs**：系统日志查询

### 5.2 响应格式

#### 5.2.1 统一响应结构
```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "code": 200,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 5.2.2 错误响应结构
```json
{
  "success": false,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "用户不存在",
    "details": "用户ID 123 不存在"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 5.2.3 分页响应结构
```json
{
  "success": true,
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 100,
      "pages": 5
    }
  }
}
```

## 6. 前后端结构设计

### 6.1 前端结构
```
frontend/
├── src/
│   ├── components/          # 通用组件
│   │   ├── ui/             # 基础UI组件
│   │   ├── chat/           # 聊天相关组件
│   │   └── agent/          # Agent相关组件
│   ├── views/              # 页面视图
│   │   ├── Chat.vue        # 主聊天页面
│   │   ├── Login.vue       # 登录页面
│   │   ├── Register.vue    # 注册页面
│   │   ├── Profile.vue     # 用户资料页面
│   │   ├── AgentConfig.vue # Agent配置页面
│   │   └── Settings.vue    # 设置页面
│   ├── stores/             # Pinia状态管理
│   │   ├── auth.ts         # 认证状态
│   │   ├── chat.ts         # 聊天状态
│   │   ├── agent.ts        # Agent状态
│   │   ├── config.ts       # 配置状态
│   │   └── user.ts         # 用户状态
│   ├── services/           # API服务
│   │   ├── api.ts          # API客户端
│   │   ├── auth.ts         # 认证API
│   │   ├── chat.ts         # 聊天API
│   │   ├── agent.ts        # Agent API
│   │   └── user.ts         # 用户API
│   ├── types/              # TypeScript类型定义
│   └── utils/              # 工具函数
└── package.json
```

### 6.2 后端结构
```
backend/
├── app/
│   ├── main.py             # 应用入口
│   ├── config.py           # 配置管理
│   └── dependencies.py     # 依赖注入
├── api/                    # API层
│   ├── v1/                 # API版本1
│   │   ├── auth.py         # 认证相关API
│   │   ├── agents.py       # Agent相关API
│   │   ├── conversations.py # 对话相关API
│   │   ├── sessions.py     # 会话相关API
│   │   ├── configs.py      # 配置相关API
│   │   ├── api_keys.py     # API密钥管理API
│   │   ├── websocket.py    # WebSocket处理
│   │   └── health.py       # 健康检查API
│   └── deps.py             # API依赖
├── services/               # 服务层
│   ├── auth_service.py     # 认证管理服务
│   ├── user_service.py     # 用户管理服务
│   ├── agent_service.py    # Agent管理服务
│   ├── conversation_service.py # 对话管理服务
│   ├── session_service.py  # 会话管理服务
│   ├── config_service.py   # 配置管理服务
│   ├── api_key_service.py  # API密钥管理服务
│   ├── quota_service.py    # 配额管理服务
│   └── monitor_service.py  # 监控管理服务
├── agents/                 # Agent层
│   ├── base_agent.py       # 基础Agent类和接口
│   ├── qa_agent.py         # 大模型问答Agent
│   ├── brainstorm_agent.py # 双模型头脑风暴Agent
│   ├── agent_manager.py    # Agent管理器
│   └── conversation_controller.py # 对话控制器
├── websocket/              # WebSocket相关
│   ├── manager.py          # WebSocket连接管理器
│   ├── router.py           # 消息路由器
│   └── handlers.py         # 消息处理器
├── data/                   # 数据层
│   ├── models/             # 数据库模型
│   │   ├── user.py         # 用户模型
│   │   ├── agent.py        # Agent模型
│   │   ├── session.py      # 会话模型
│   │   ├── conversation.py # 对话模型
│   │   ├── config.py       # 配置模型
│   │   └── api_key.py      # API密钥模型
│   ├── schemas/            # Pydantic模型
│   │   ├── user.py         # 用户Schema
│   │   ├── agent.py        # Agent Schema
│   │   ├── session.py      # 会话Schema
│   │   ├── conversation.py # 对话Schema
│   │   ├── config.py       # 配置Schema
│   │   └── api_key.py      # API密钥Schema
│   └── database.py         # 数据库连接
├── core/                   # 核心功能
│   ├── auth.py             # 认证授权
│   ├── config.py           # 配置管理
│   ├── exceptions.py       # 异常定义
│   ├── security.py         # 安全相关
│   ├── encryption.py       # 加密解密
│   ├── quota.py            # 配额管理
│   ├── logging.py          # 日志管理
│   └── middleware.py       # 中间件
└── tests/                  # 测试
    ├── unit/               # 单元测试
    ├── integration/        # 集成测试
    └── fixtures/           # 测试数据
```

## 7. 开发阶段规划

### 7.1 第一阶段：基础框架（4周）
- 搭建项目基础架构
- 实现用户注册、登录、认证系统
- 建立完整的数据库结构
- 实现基础的聊天界面
- 完成Agent切换功能
- 实现基础的错误处理和日志系统

### 7.2 第二阶段：核心功能（6周）
- 实现大模型问答Agent（标准对话界面）
- 实现双模型头脑风暴Agent（多模型讨论界面）
- 完善对话管理功能
- 添加会话管理功能
- 实现Agent配置管理
- 实现用户资料管理
- 完善API接口和错误处理

### 7.3 第三阶段：高级功能（4周）
- 完善Agent配置界面
- 添加对话导出和分享
- 优化用户界面体验
- 完善监控和日志系统
- 实现系统健康检查
- 添加性能监控

### 7.4 第四阶段：优化扩展（4周）
- 性能优化和缓存策略
- 添加更多Agent类型
- 完善文档和测试
- 用户体验优化
- 系统稳定性优化
- 安全性增强

## 8. 页面设计风格

### 8.1 设计理念
- **模仿主流AI官网**：参考OpenAI、Claude等官网的交互设计
- **简洁现代**：采用现代化的UI设计风格
- **响应式布局**：支持桌面端和移动端
- **暗色主题**：支持明暗主题切换

### 8.2 主要页面
- **登录页面**：用户登录界面
- **注册页面**：用户注册界面
- **聊天主页面**：模仿OpenAI的聊天界面，左侧Agent选择，中间对话区域
- **用户资料页面**：用户信息管理和设置
- **Agent配置页面**：提供大模型参数配置界面
- **设置页面**：用户偏好和系统设置

### 8.3 不同Agent的页面交互形式

#### 8.3.1 大模型问答Agent页面
- **标准对话界面**：用户输入问题，AI回答
- **流式响应**：实时显示AI生成的内容
- **历史记录**：显示完整的对话历史

#### 8.3.2 双模型头脑风暴Agent页面
- **初始输入界面**：用户输入背景信息和讨论主题
- **双模型讨论展示**：两个模型互相讨论的交流展示
- **多轮对话**：支持多轮头脑风暴讨论
- **讨论总结**：提供讨论结果的总结和建议

## 9. 安全设计

### 9.1 认证授权
- **JWT Token认证**：使用RS256算法签名，支持Token刷新
- **基础用户身份验证**：用户名/邮箱+密码登录
- **安全的会话管理**：WebSocket连接认证和会话隔离
- **用户ID区分个人数据**：严格的数据访问权限控制
- **密码加密存储**：使用bcrypt哈希算法
- **Token过期和刷新机制**：访问Token 15分钟过期，刷新Token 7天过期

### 9.2 API密钥安全管理
```python
class APIKeyManager:
    """API密钥安全管理器"""

    def __init__(self, encryption_key: bytes):
        self.fernet = Fernet(encryption_key)

    def encrypt_api_key(self, api_key: str) -> str:
        """加密API密钥"""
        return self.fernet.encrypt(api_key.encode()).decode()

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """解密API密钥"""
        return self.fernet.decrypt(encrypted_key.encode()).decode()

    async def validate_api_key(self, provider: str, api_key: str) -> bool:
        """验证API密钥有效性"""
        # 根据不同提供商验证API密钥
        validators = {
            "openai": self._validate_openai_key,
            "anthropic": self._validate_anthropic_key,
            "custom": self._validate_custom_key
        }

        validator = validators.get(provider)
        if validator:
            return await validator(api_key)
        return False
```

### 9.3 用户配额和成本控制
```python
class UsageQuotaManager:
    """用户使用配额管理器"""

    async def check_quota(self, user_id: str, operation: str) -> bool:
        """检查用户配额"""
        quota = await self._get_user_quota(user_id)
        usage = await self._get_current_usage(user_id)

        return usage[operation] < quota[operation]

    async def record_usage(self, user_id: str, operation: str, cost: float):
        """记录用户使用量"""
        await self._update_usage_stats(user_id, operation, cost)

        # 检查是否超出配额
        if not await self.check_quota(user_id, operation):
            await self._notify_quota_exceeded(user_id, operation)

    async def get_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """获取用户使用统计"""
        return await self._get_usage_statistics(user_id)
```

### 9.4 数据安全
- **敏感数据加密存储**：API密钥使用Fernet对称加密
- **HTTPS加密传输**：所有API通信强制使用HTTPS
- **输入验证和过滤**：使用Pydantic进行严格的数据验证
- **SQL注入防护**：使用SQLAlchemy ORM和参数化查询
- **XSS攻击防护**：前端输入过滤和输出转义
- **CSRF攻击防护**：SameSite Cookie和CSRF Token

### 9.5 系统安全
- **请求频率限制**：基于用户和IP的速率限制
- **异常访问监控**：记录和分析异常访问模式
- **安全日志记录**：详细的安全事件日志
- **数据备份和恢复**：定期数据备份和灾难恢复计划
- **权限最小化原则**：用户只能访问授权的Agent和数据

### 9.6 WebSocket安全
```python
class WebSocketSecurity:
    """WebSocket安全管理"""

    async def authenticate_websocket(self, websocket: WebSocket, token: str) -> Optional[str]:
        """WebSocket连接认证"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["RS256"])
            user_id = payload.get("sub")

            # 验证用户是否存在且活跃
            user = await self._get_user(user_id)
            if user and user.is_active:
                return user_id

        except jwt.InvalidTokenError:
            pass

        return None

    async def authorize_session_access(self, user_id: str, session_id: str) -> bool:
        """验证用户对会话的访问权限"""
        session = await self._get_session(session_id)
        return session and session.user_id == user_id
```

## 10. 监控和运维

### 10.1 系统监控
- **健康检查**：系统状态监控
- **性能监控**：响应时间和吞吐量
- **错误监控**：异常和错误日志
- **资源监控**：CPU、内存、磁盘使用

### 10.2 日志管理
- **访问日志**：用户访问记录
- **错误日志**：系统错误记录
- **安全日志**：安全事件记录
- **业务日志**：业务操作记录

### 10.3 数据备份
- **数据库备份**：定期数据备份
- **文件备份**：用户文件备份
- **配置备份**：系统配置备份
- **恢复机制**：数据恢复流程

## 11. 测试策略

### 11.1 测试类型
- **单元测试**：各模块功能测试
- **集成测试**：模块间接口测试
- **端到端测试**：完整业务流程测试
- **性能测试**：系统性能压力测试

### 11.2 测试覆盖
- **API接口测试**：所有接口功能测试
- **Agent功能测试**：AI功能测试
- **用户界面测试**：前端交互测试
- **安全测试**：安全漏洞测试

## 12. 后期优化规划

### 12.1 中优先级优化项
- **缓存策略优化**：实现智能的对话历史缓存和Agent配置缓存
- **双模型头脑风暴控制逻辑完善**：
  - 实现讨论质量评估机制
  - 添加讨论收敛性检测
  - 支持不同讨论风格（协作式、辩论式）
- **用户配额管理系统**：
  - 基于用户等级的配额分配
  - 实时使用量监控和告警
  - 成本统计和计费功能
- **数据库升级路径**：
  - SQLite到PostgreSQL的迁移方案
  - 数据库连接池优化
  - 读写分离架构

### 12.2 低优先级扩展项
- **Agent插件系统**：
  - 动态Agent加载机制
  - Agent市场和分享功能
  - 第三方Agent开发SDK
- **高级性能监控**：
  - 详细的性能指标收集
  - 实时监控仪表板
  - 自动性能优化建议
- **企业级功能**：
  - 多租户支持
  - 企业SSO集成
  - 高级权限管理
  - 审计日志系统

### 12.3 技术债务管理
- **代码质量**：定期代码审查和重构
- **测试覆盖率**：目标达到80%以上的测试覆盖率
- **文档维护**：保持API文档和架构文档的同步更新
- **依赖管理**：定期更新依赖包和安全补丁

## 13. 总结

本架构设计文档为AI Agent基座平台提供了清晰的技术路线图和功能规划。平台专注于两个核心Agent：大模型问答和双模型头脑风暴，支持灵活的Agent配置管理，采用现代化的技术栈和模仿主流AI官网的设计风格。

### 13.1 核心改进
- **完善的数据库设计**：支持用户Agent权限管理和配置分层
- **标准化的Agent接口**：确保系统可扩展性和一致性
- **安全的API密钥管理**：加密存储和权限控制
- **实时通信架构**：WebSocket支持流式响应和多模型交互
- **全面的安全设计**：从认证到数据保护的完整安全体系

### 13.2 开发建议
开发团队可以按照四个阶段的规划，优先实现高优先级的核心功能，逐步完善平台的各项能力，最终构建一个功能完善、用户体验优良、安全可靠的AI应用平台。

建议在开发过程中：
1. 严格按照Agent接口标准实现所有Agent
2. 优先实现WebSocket实时通信功能
3. 重视安全设计的每个细节
4. 保持代码质量和测试覆盖率
