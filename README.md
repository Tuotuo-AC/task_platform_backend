# Task Platform API

任务协作平台后端 API，基于 FastAPI + MySQL + Redis + Celery + DeepSeek 构建。支持用户认证、任务管理、项目协作、评论通知、WebSocket 实时推送和 AI 辅助功能。

## ✨ 主要功能

- 🔐 **用户认证**：JWT 双令牌（Access/Refresh Token），支持注册、登录、令牌刷新。
- 📋 **任务管理**：创建、更新、删除、分页列表，支持按状态、优先级、指派人过滤，按截止日期/优先级等排序。
- 👥 **项目协作**：项目创建、成员管理（多对多关联）。
- 💬 **评论系统**：对任务发表评论，自动为任务负责人和指派人创建通知记录。
- 🔔 **实时通知**：WebSocket + Redis Pub/Sub，任务指派、状态变更时实时推送通知。
- 🤖 **AI 智能功能**：
  - 智能任务拆解：根据任务标题/描述，自动生成子任务建议。
  - 每日工作摘要：异步生成当日任务摘要，存入通知中心（支持 Celery 定时调度）。
- 🐳 **容器化部署**：Docker Compose 一键启动，集成 FastAPI + MySQL + Redis + Celery Worker + Celery Beat。

## 🛠 技术栈

| 组件            | 技术                                                         |
|----------------|--------------------------------------------------------------|
| Web 框架        | FastAPI                                                      |
| ORM             | SQLAlchemy 2.0                                               |
| 数据库          | MySQL 8.0                                                    |
| 缓存/消息队列   | Redis (用于缓存、Pub/Sub、Celery broker/backend)             |
| 认证            | JWT (python-jose) + bcrypt                                   |
| 异步任务        | Celery                                                       |
| AI 服务         | DeepSeek API                                                 |
| 部署            | Docker / Docker Compose                                      |

## 📁 项目结构

```
task-platform/
├── app/
│   ├── core/               # 配置、数据库、安全、依赖、Redis、Celery
│   ├── models/             # SQLAlchemy 模型（User, Task, Project, Comment, Notification）
│   ├── schemas/            # Pydantic 模型（输入/输出验证）
│   ├── routers/            # API 路由（auth, users, tasks, projects, comments, notifications, ai）
│   ├── services/           # 业务逻辑（AI 服务等）
│   ├── tasks/              # Celery 异步任务（AI 摘要生成）
│   ├── utils/              # WebSocket 连接管理
│   └── main.py             # 应用入口
├── tests/                  # 单元测试
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 快速开始（本地开发）

### 前提条件

- Python 3.10+
- Docker (可选，用于运行 MySQL/Redis)
- DeepSeek API Key（[申请地址](https://platform.deepseek.com/)）

### 1. 克隆项目

```bash
git clone https://github.com/Tuotuo-AC/task-platform.git
cd task-platform
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，并填写真实值：

```env
DATABASE_URL=mysql+pymysql://task_user:task_pass@localhost:3307/task_db
REDIS_URL=redis://localhost:6380/0
SECRET_KEY=your-random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

> 注意：`DATABASE_URL` 和 `REDIS_URL` 中的端口请根据你的 Docker 映射端口调整（见下文）。

### 4. 启动 MySQL 和 Redis（使用 Docker）

```bash
docker-compose up -d mysql redis
```

默认端口映射：
- MySQL: 宿主机 `3307` → 容器 `3306`
- Redis: 宿主机 `6380` → 容器 `6379`

### 5. 运行 FastAPI 应用

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000/docs` 查看自动生成的 API 文档。

### 6. （可选）启动 Celery Worker 和 Beat

在另外的终端中：

```bash
celery -A app.core.celery_app worker --loglevel=info
celery -A app.core.celery_app beat --loglevel=info
```

## 🐳 Docker 生产部署

### 1. 准备 `.env` 文件

确保 `.env` 中包含以下变量（无需写 `DATABASE_URL` 和 `REDIS_URL`，服务内部会覆盖）：

```env
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DEEPSEEK_API_KEY=...
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

### 2. 构建并启动所有服务

```bash
docker-compose up --build
```

服务包括：
- `mysql` (端口 3306)
- `redis` (端口 6379)
- `app` (FastAPI, 端口 8000)
- `celery_worker` (后台任务)
- `celery_beat` (定时调度)

### 3. 访问 API 文档

`http://localhost:8000/docs`

## 📡 API 使用示例

### 注册用户

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "alice",
  "password": "123456"
}
```

### 登录获取 Token

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "alice",
  "password": "123456"
}
```

响应：
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

### 创建任务（需要认证）

```http
POST /api/tasks/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "实现用户认证模块",
  "priority": "high"
}
```

### AI 智能拆解子任务

```http
POST /api/ai/tasks/{task_id}/subtasks
Authorization: Bearer <access_token>
```

响应示例：
```json
{
  "task_id": 1,
  "suggested_subtasks": [
    "设计数据库表结构",
    "实现注册接口",
    "实现登录 JWT 签发",
    "添加刷新令牌逻辑"
  ]
}
```

## 🔌 WebSocket 实时通知

连接地址：
```
ws://localhost:8000/api/ws/notifications?token=<access_token>
```

连接后，当任务被指派或状态变更时，会收到类似消息：
```
You have been assigned to task '实现用户认证模块'
```

## 🧪 运行测试

```bash
pytest tests/ -v
```

## 📊 数据库表

- `users` – 用户信息
- `tasks` – 任务
- `projects` – 项目
- `project_members` – 项目-成员关联表
- `comments` – 评论
- `notifications` – 通知记录

## ⚠️ 注意事项

- 生产环境务必修改 `SECRET_KEY` 为强随机值，并妥善保管。
- DeepSeek API Key 请勿提交到版本控制。
- Celery Beat 默认每分钟执行一次 `generate_daily_summary_for_all_users`（开发测试用）。生产环境请修改 `celery_app.py` 中的 `beat_schedule` 为 `crontab(minute=0, hour=8)`。
- 由于 `redis-py` 是同步库，在本地开发时需要在 `lifespan` 中将 `listen_redis_and_forward` 放在独立线程中运行（项目已处理）。
