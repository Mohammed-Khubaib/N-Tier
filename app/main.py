from fastapi import FastAPI
from .database import engine, Base
from .routers import users_router, projects_router, tasks_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Management API",
    description="A comprehensive task management system with users, projects, and tasks",
    version="1.0.0",
)

# Include routers
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(tasks_router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Task Management API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}