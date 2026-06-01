from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

security = HTTPBearer()

# 依赖注入函数：负责从HTTP请求中提取JWT令牌、验证令牌有效性
def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
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
    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=401,detail='Invalid token payload')
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401,detail='User not found or inactive')
        return user