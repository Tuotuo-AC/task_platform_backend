from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from app.core.dependencies import get_current_user
from app.core.redis_client import publish_notification  # 用于发送Redis实时通知

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# 创建任务
@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_task = Task(**task_data.model_dump(), owner_id=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    if new_task.assignee_id and new_task.assignee_id != current_user.id:
        publish_notification("notifications", f"{new_task.assignee_id}:You have been assigned to task '{new_task.title}'")
    return new_task

# 列出任务 GET/ 分页、过滤、排序
@router.get("/", response_model=List[TaskOut])
def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assignee_id: Optional[int] = None,
    sort_by: Optional[str] = Query(None, regex="^(created_at|due_date|priority)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Task).filter(
        (Task.owner_id == current_user.id) | (Task.assignee_id == current_user.id)
    )
    # 过滤
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    # 排序
    if sort_by:
        column = getattr(Task, sort_by)
        if order == "desc":
            column = column.desc()
        query = query.order_by(column)
    else:
        query = query.order_by(Task.created_at.desc())
    # 分页
    tasks = query.offset(skip).limit(limit).all()
    return tasks

# 获取单个任务
@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    # 任务不存在返回404
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # 用户无权限返回403
    if task.owner_id != current_user.id and task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return task

# 更新任务
@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can update task")
    old_status = task.status
    for key, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    if task.assignee_id and task.status != old_status:
        publish_notification("notifications", f"{task.assignee_id}:Task '{task.title}' status changed from {old_status} to {task.status}")
    return task

# 删除任务
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can delete task")
    db.delete(task)
    db.commit()
    return None

# 指派任务
@router.patch("/{task_id}/assign")
def assign_task(
    task_id: int,
    assignee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 验证指派人是否存在
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can assign task")
    assignee = db.query(User).filter(User.id == assignee_id).first()
    if not assignee:
        raise HTTPException(status_code=404, detail="Assignee not found")
    task.assignee_id = assignee_id
    db.commit()
    publish_notification("notifications", f"{assignee_id}:You have been assigned to task '{task.title}'")
    return {"message": f"Task assigned to {assignee.username}"}