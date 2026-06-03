from fastapi import APIRouter, Depends
from app.schemas.user import UserOut
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

# 获取当前登录用户的信息
@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user