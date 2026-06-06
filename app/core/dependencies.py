from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

# HTTPBearer()是FastAPI提供的安全工具，自动从请求头提取Authorization: Bearer<token>里的token
security = HTTPBearer()

# 依赖注入函数：负责从HTTP请求中提取JWT令牌、验证令牌有效性
def get_current_user(
# 依赖注入，FastAPI 会自动调用 security 函数，从请求头取出 token 并封装到 credentials 对象中。
        credentials: HTTPAuthorizationCredentials = Depends(security),
        # 依赖注入数据库会话，用于查询用户
        db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    if not payload or payload.get('type') != 'access':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired token.',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    # 提取用户ID并查询数据库
    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=401,detail='Invalid token payload')
    user = db.query(User).filter(User.id == int(user_id)).first()
    # 检查用户状态
    if not user or not user.is_active:
        raise HTTPException(status_code=401,detail='User not found or inactive')
    # 认证通过，返回当前登录的用户对象
    return user