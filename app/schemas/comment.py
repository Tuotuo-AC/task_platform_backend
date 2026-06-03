from pydantic import BaseModel
from datetime import datetime

# 创建评论的请求体
class CommentCreate(BaseModel):
    content: str

# 返回评论的响应体
class CommentOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    user_id: int
    task_id: int

    class Config:
        from_attributes = True