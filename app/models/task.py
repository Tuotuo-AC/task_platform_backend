from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from app.core.database import Base
import enum

# 继承自(str, enum.Enum)，枚举值既是字符串又是枚举成员
class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    # 状态枚举
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    # 优先级枚举，默认MEDIUM
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    # 复合索引：在 (assignee_id, status) 两列上建立一个索引，名为 ix_tasks_assignee_status
    __table_args__ = (
        Index("ix_tasks_assignee_status", "assignee_id", "status"),
    )