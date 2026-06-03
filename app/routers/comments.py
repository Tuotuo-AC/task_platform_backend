from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.comment import Comment
from app.models.task import Task
from app.models.user import User
from app.models.notification import Notification
from app.schemas.comment import CommentCreate, CommentOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/tasks/{task_id}", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(
    task_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    comment = Comment(
        content=comment_data.content,
        user_id=current_user.id,
        task_id=task_id
    )
    db.add(comment)
    # 确定需要通知的用户（任务创建者和指派人，排除自己）
    notify_users = set()
    if task.owner_id != current_user.id:
        notify_users.add(task.owner_id)
    if task.assignee_id and task.assignee_id != current_user.id:
        notify_users.add(task.assignee_id)
    for uid in notify_users:
        notification = Notification(
            message=f"{current_user.username} commented on task '{task.title}': {comment_data.content[:50]}",
            user_id=uid,
            related_task_id=task_id
        )
        db.add(notification)
    db.commit()
    db.refresh(comment)
    return comment

@router.get("/tasks/{task_id}", response_model=List[CommentOut])
def get_task_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id and task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission to view comments")
    comments = db.query(Comment).filter(Comment.task_id == task_id).order_by(Comment.created_at).all()
    return comments