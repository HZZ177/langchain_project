# AI Agent Platform

一个企业级AI智能体基座平台，提供统一的Web界面来管理和使用各种AI Agent，支持多种业务场景的智能化应用。

## ✨ 特性

- 🤖 **多Agent支持** - 支持问答、分析、创作等多种类型的AI智能体
- 🔄 **实时对话** - 基于WebSocket的流式响应，提供流畅的对话体验
- 🚀 **高性能** - 预热式连接池设计，显著提升响应速度
- 👥 **多用户管理** - 完整的用户认证和权限管理系统
- 📊 **会话管理** - 支持多会话并行，历史记录持久化
- 🔧 **灵活配置** - 支持Agent个性化配置和参数调优
- 📈 **监控面板** - 实时连接池状态监控和性能统计

## 🏗️ 技术架构

### 前端
- **Vue 3** + **TypeScript** - 现代化前端框架
- **Tailwind CSS** - 原子化CSS框架
- **Pinia** - 状态管理
- **WebSocket** - 实时通信

### 后端
- **FastAPI** - 高性能Python Web框架
- **SQLAlchemy** - ORM数据库操作
- **LangChain** - AI应用开发框架
- **SQLite** - 轻量级数据库
- **Loguru** - 统一日志管理

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd langchain_project
```

2. **后端设置**
```bash
cd backend
pip install -r requirements.txt
```

3. **前端设置**
```bash
cd frontend
npm install
```

4. **启动服务**

后端服务：
```bash
cd backend
python main.py
```

前端服务：
```bash
cd frontend
npm run dev
```

5. **访问应用**
- 前端界面: http://localhost:3000
- API文档: http://localhost:8000/docs
- 连接池监控: http://localhost:8000/api/v1/pool/stats

### 默认账号

- 用户名: `admin`
- 密码: `admin123`

## 📱 功能模块

### 🔐 用户管理
- 用户注册/登录
- JWT Token认证
- 权限控制

### 🤖 Agent管理
- 智能问答Agent
- Agent配置管理
- 多Agent切换

### 💬 对话系统
- 实时流式对话
- 多会话管理
- 历史记录查看

### 📊 监控面板
- 连接池状态监控
- 性能统计分析
- 系统健康检查

## 🔧 配置说明

### 环境配置

主要配置项位于 `backend/config.py`：

- **数据库配置** - SQLite数据库路径
- **JWT配置** - Token密钥和过期时间
- **AI模型配置** - 默认模型参数
- **管理员账号** - 初始管理员信息

### Agent配置

每个Agent支持独立配置：
- 模型选择 (GPT-3.5, GPT-4等)
- 温度参数
- 最大Token数
- 系统提示词
- API密钥

## 📈 性能优化

### 连接池技术
- 预热式LLM连接池
- 每个Agent预创建5个连接实例
- 自动连接回收和清理
- 显著减少首次响应时间

### 响应时间
- 首次对话: ~500ms (预热后)
- 后续对话: ~100-300ms
- WebSocket实时通信

## 🛠️ 开发指南

### 项目结构
```
langchain_project/
├── backend/                 # 后端服务
│   ├── agents/             # Agent实现
│   ├── api/                # REST API
│   ├── core/               # 核心功能
│   ├── data/               # 数据模型
│   ├── services/           # 业务服务
│   └── websocket/          # WebSocket处理
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/     # UI组件
│   │   ├── views/          # 页面组件
│   │   ├── stores/         # 状态管理
│   │   └── services/       # API服务
└── README.md
```

### 添加新Agent

1. 继承 `BaseAgent` 类
2. 实现 `process_message` 方法
3. 在 `AgentManager` 中注册
4. 配置数据库模型

## 🔍 API文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的API文档。

主要API端点：
- `/api/v1/auth/*` - 认证相关
- `/api/v1/agents/*` - Agent管理
- `/api/v1/sessions/*` - 会话管理
- `/api/v1/pool/*` - 连接池监控
- `/ws` - WebSocket连接
