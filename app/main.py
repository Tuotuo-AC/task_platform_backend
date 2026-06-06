from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio
import threading
from app.core.database import engine, Base
from app.routers import auth, users, tasks, projects, comments, notifications, ai
from app.utils.websocket_manager import listen_redis_and_forward

def run_redis_listener():
    """在单独的线程中运行 Redis 订阅转发器"""
    asyncio.run(listen_redis_and_forward())

# 生命周期管理lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 创建数据库表（同步操作，不会阻塞太久）
    Base.metadata.create_all(bind=engine)
    # 启动 Redis 监听线程（不阻塞主事件循环）
    thread = threading.Thread(target=run_redis_listener, daemon=True)
    thread.start()
    yield

app = FastAPI(title="Task Platform API", version="2.0.0", lifespan=lifespan)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(ai.router, prefix="/api")

# 简单的 GET 接口，用于负载均衡器或容器编排系统检测服务是否存活
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Service is running"}