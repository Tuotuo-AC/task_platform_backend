from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
# from sqlalchemy import Index

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    # # 查询某个任务的所有评论并按时间排序时，可高效利用索引。
    #     __table_args__ = (
    #         Index("ix_comments_task_id_created", "task_id", "created_at"),
    #     )


