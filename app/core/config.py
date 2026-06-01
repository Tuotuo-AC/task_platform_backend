# 该配置文件用于从环境变量（.env）中读取敏感信息

import os
from dotenv import load_dotenv

# 加载.env文件中的变量到os.environ
load_dotenv()

class Settings:
    # 数据库连接URL, 从环境变量读取， 默认None会报错
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    # Redis连接URL
    REDIS_URL: str = os.getenv("REDIS_URL")
    # JWT 密钥
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    # JWT 算法
    ALGORITHM: str = os.getenv("ALGORITHM")
    # ACCESS Token 过期时间（分钟）
    # os.getenv() 返回字符串，而我们需要整数用于时间计算。如果环境变量缺失，int(None) 会报错，所以需要转换成int，提供默认值避免None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30))
    # Refresh Token 过期时间（天）
    ACCESS_TOKEN_EXPIRE_DAYS: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS",7))
    # Deepseek API KEY
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY")
    # Deepseek API 基础URL(带默认值)
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL",'https://api.deepseek.com/v1')

# 创建全局实例，方便其他模块导入
settings = Settings()