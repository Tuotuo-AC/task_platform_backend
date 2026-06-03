from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.task import TaskStatus, TaskPriority

# 创建任务的请求体
class TaskCreate(BaseModel):
    # 请求体 JSON 必须包含 title，其他字段可选
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None
    project_id: Optional[int] = None

# 更新任务的请求体
class TaskUpdate(BaseModel):
    # 可以只发送需要修改的字段，未提供的字段保持原值不变
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None
    project_id: Optional[int] = None

# 返回任务信息的响应体
class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    owner_id: int
    assignee_id: Optional[int]
    project_id: Optional[int]

    class Config:
        from_attributes = True