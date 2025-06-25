from .user import User, UserCreate, UserUpdate, UserWithProjects, UserWithTasks
from .project import Project, ProjectCreate, ProjectUpdate, ProjectWithTasks, ProjectWithOwner
from .task import Task, TaskCreate, TaskUpdate, TaskWithProject, TaskWithAssignee

# Update forward references
UserWithProjects.model_rebuild()
UserWithTasks.model_rebuild()
ProjectWithTasks.model_rebuild()
ProjectWithOwner.model_rebuild()
TaskWithProject.model_rebuild()
TaskWithAssignee.model_rebuild()

__all__ = [
    "User", "UserCreate", "UserUpdate", "UserWithProjects", "UserWithTasks",
    "Project", "ProjectCreate", "ProjectUpdate", "ProjectWithTasks", "ProjectWithOwner",
    "Task", "TaskCreate", "TaskUpdate", "TaskWithProject", "TaskWithAssignee"
]