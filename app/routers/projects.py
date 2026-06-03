from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.project import Project, project_members
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    # 将创建者自动加入项目成员表
    db.execute(project_members.insert().values(project_id=new_project.id, user_id=current_user.id))
    db.commit()
    return new_project

@router.get("/", response_model=List[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    projects = db.query(Project).join(project_members).filter(project_members.c.user_id == current_user.id).all()
    return projects

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    # 先查找项目
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    is_member = db.execute(project_members.select().where(
        project_members.c.project_id == project_id,
        project_members.c.user_id == current_user.id
    )).first()
    # 检查当前用户是否是成员
    if not is_member and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    return project

@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # 只有项目所有者可以更新项目名称或描述
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can update project")
    for key, value in project_data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project

@router.post("/{project_id}/members/{user_id}")
def add_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can add members")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    existing = db.execute(project_members.select().where(
        project_members.c.project_id == project_id,
        project_members.c.user_id == user_id
    )).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already in project")
    db.execute(project_members.insert().values(project_id=project_id, user_id=user_id))
    db.commit()
    return {"message": f"User {user.username} added to project {project.name}"}