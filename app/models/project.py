from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# 项目与用户之间多对多关系的辅助表project_members
project_members = Table(
    "project_members",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id")),
    Column("user_id", Integer, ForeignKey("users.id"))
)

# 项目模型
class Project(Base):
    __tablename__ = "projects"
    # 自增主键
    id = Column(Integer, primary_key=True, index=True)
    # 项目名称，必填
    name = Column(String(100), nullable=False)
    # 项目描述，可选，最长500字符
    description = Column(String(500), nullable=True)
    # 项目创建者（所有者）的用户 ID，外键关联 users.id，非空
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # 创建时间，由数据库自动填充
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # 更新时间，记录修改时自动更新
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    members = relationship("User", secondary=project_members, backref="projects")