from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
# from sqlalchemy import Index

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    # 通知的文本内容
    message = Column(String(500), nullable=False)
    is_read = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    related_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 索引优化
    # __table_args__ = (
    #     Index("ix_notifications_user_read", "user_id", "is_read"),  # 加速“查询未读通知”
    #     Index("ix_notifications_user_created", "user_id", "created_at"), # 加速“按时间列出通知”
    # )
