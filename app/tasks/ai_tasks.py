from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.task import Task
from app.models.notification import Notification
from app.services.ai_service import generate_daily_summary
from datetime import datetime, timedelta

# 为指定用户生成当天的任务工作摘要，并保存为一条未读通知
@celery_app.task
def generate_daily_summary_for_user(user_id: int):
    # 创建数据库会话
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        # 用户不存在直接返回
        if not user:
            return
        # 确定当天的时间范围
        today_start = datetime.now().replace(hour=0, minute=0, second=0)
        today_end = today_start + timedelta(days=1)
        # 查询任务
        tasks = db.query(Task).filter(
            (Task.assignee_id == user_id) | (Task.owner_id == user_id),
            Task.created_at >= today_start,
            Task.created_at < today_end
        ).all()
        # 构造任务数据
        task_data = [{"title": t.title, "status": t.status.value} for t in tasks]
        # 调用AI生成摘要
        summary = generate_daily_summary(user.username, task_data)
        # 创建通知记录
        notification = Notification(
            message=f"📅 今日工作摘要：{summary}",
            user_id=user_id,
            is_read=False
        )
        # 提交到数据库
        db.add(notification)
        db.commit()
    finally:
        db.close()

# 批量触发所有用户的摘要生成
@celery_app.task
def generate_daily_summary_for_all_users():
    db = SessionLocal()
    try:
        user_ids = db.query(User.id).filter(User.is_active == True).all()
        for (user_id,) in user_ids:
            generate_daily_summary_for_user.delay(user_id)
    finally:
        db.close()