from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# 用户注册时的请求体
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

# 用户登录时的请求体
class UserLogin(BaseModel):
    username: str
    password: str

# 返回用户信息时的响应体
class UserOut(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# 登录成功返回的 JWT 令牌
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"