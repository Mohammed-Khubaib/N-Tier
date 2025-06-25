from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from ..models.project import ProjectStatus

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    owner_id: int

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None

class Project(ProjectBase):
    id: int
    status: ProjectStatus
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProjectWithTasks(Project):
    tasks: List["Task"] = []

class ProjectWithOwner(Project):
    owner: "User"

# Only call after imports are resolved
from .task import Task
from .user import User
ProjectWithTasks.model_rebuild()
ProjectWithOwner.model_rebuild()
