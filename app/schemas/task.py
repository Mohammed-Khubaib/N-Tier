from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..models.task import TaskStatus, TaskPriority

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    project_id: int
    assignee_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    is_completed: Optional[bool] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None

class Task(TaskBase):
    id: int
    status: TaskStatus
    is_completed: bool
    project_id: int
    assignee_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TaskWithProject(Task):
    project: "Project"

class TaskWithAssignee(Task):
    assignee: Optional["User"] = None

# Resolve forward refs after class definitions
from .project import Project
from .user import User
TaskWithProject.model_rebuild()
TaskWithAssignee.model_rebuild()
