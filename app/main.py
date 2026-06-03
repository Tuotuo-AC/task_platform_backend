from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio
from app.core.database import engine, Base
from app.routers import auth, users, tasks, projects, comments, notifications, ai
from app.utils.websocket_manager import listen_redis_and_forward


# 生命周期管理lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    asyncio.create_task(listen_redis_and_forward())
    yield

app = FastAPI(title="Task Platform API", version="2.0.0", lifespan=lifespan)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(ai.router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Service is running"}