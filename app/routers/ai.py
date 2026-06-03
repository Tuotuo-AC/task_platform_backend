from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.task import Task
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.ai_service import suggest_subtasks
from app.tasks.ai_tasks import generate_daily_summary_for_user

router = APIRouter(prefix="/ai", tags=["AI"])

# 智能任务拆解：根据已有任务的标题和描述，调用 DeepSeek API 生成子任务建议列表
@router.post("/tasks/{task_id}/subtasks")
def get_subtask_suggestions(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    # 查询任务
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # 权限校验
    if task.owner_id != current_user.id and task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission")
    subtasks = suggest_subtasks(task.title, task.description or "")
    return {"task_id": task_id, "suggested_subtasks": subtasks}

# 触发每日摘要：异步生成当前用户的当日工作摘要，结果会以通知形式推送给用户
@router.post("/summary/trigger")
def trigger_daily_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    generate_daily_summary_for_user.delay(current_user.id)
    return {"message": "Summary generation started, will be delivered as notification soon."}