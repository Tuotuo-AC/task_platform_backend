# 1.创建 SQLAlchemy 引擎（engine）和会话工厂（SessionLocal）。
# 2.定义基类 Base，所有模型继承它。
# 3.提供依赖函数 get_db()，用于 FastAPI 路径函数中获取数据库会话。


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# engine：负责连接数据库、执行 SQL。配置了连接池和自动重连。
# 创建数据库引擎，pool_pre_ping=True 会在使用前检测连接是否有效
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 连接前先ping一下，避免使用已断开的连接
    pool_recycle=3600,   # 每小时回收连接，避免MYSQL超时断开
)

# 会话工厂
# SessionLocal：用于创建新的数据库会话对象，每个请求应该使用独立的会话。
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 模型基类
# 所有模型类的父类，SQLAlchemy 通过它知道哪些类要映射到数据库表。
Base = declarative_base()

# 一个生成器函数，使用 yield 提供会话，确保请求结束后关闭会话。FastAPI 的 Depends 会管理它的生命周期。
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





