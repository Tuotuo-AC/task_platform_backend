from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "task_platform",           # 应用名称
    broker=settings.REDIS_URL,      # 消息代理（broker），用于存储待执行的任务
    backend=settings.REDIS_URL,     # 结构后端，用于存储任务执行结果
    include=['app.task.ai_tasks']   # 启动时要导入的任务模块列表
)


celery_app.conf.update(
    task_serializer="json",        # 任务消息的序列化格式
    accept_content=["json"],       # 只接受 JSON 格式的消息（安全性）
    result_serializer="json",      # 任务结果的序列化格式
    timezone="Asia/Shanghai",      # 时区设置（影响定时任务的时间）
    enable_utc=False,              # 不使用 UTC 时间，使用上面指定的时区
    beat_schedule={                # 定时任务配置（Celery Beat 会读取）
        "generate-daily-summary": {
            "task": "app.tasks.ai_tasks.generate_daily_summary_for_all_users",
            "schedule": 60.0,      # 每 60 秒执行一次
        },
    },
)