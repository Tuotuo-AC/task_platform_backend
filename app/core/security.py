"""
1.密码安全：把用户密码变成不可逆的哈希值存储。
2.生成和验证 JWT：用于用户登录后发放令牌，后续请求携带令牌即可认证。
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings

# 创建一个CryptContext 对象，告诉它我们使用bcrypt算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 验证密码
def verify_password(plain_password:str, hashed_password:str) -> bool:
    """用户登录时,用此函数比对输入的密码和数据库里的哈希"""
    return pwd_context.verify(plain_password, hashed_password) # pwd_context.verify内部从hashed_password中提取盐，重新哈希plain_passwprd对比是否一致

# 生成密码哈希
def get_password_hash(password:str) -> str:
    """用户注册时,将原始密码转为哈希值存入数据库"""
    return pwd_context.hash(password)

# 生成短期访问令牌（有效期短（如30分钟），减少泄露风险，需要频繁刷新。）
def create_access_token(data: dict, expires_delta: timedelta = None):
    # 复制一份原始数据，避免修改传入的字典
    to_encode = data.copy()
    # 计算过期时间
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    # 添加过期时间戳和字段access用于区分
    to_encode.update({"exp": expire,'type':'access'})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# 生成长期刷新令牌（有效期长，仅用于换取新的 access token，单独存储或放在更安全的地方）
def create_refresh_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    # 复制原始数据
    to_encode = data.copy()
    # 字段为refresh用于区分
    to_encode.update({"exp": expire,'type':'refresh'})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# 解码并验证令牌
def decode_token(token:str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # 解码成功返回字典
        return payload
    except JWTError:
        # 解码失败捕获异常并返回None
        return None





