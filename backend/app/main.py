# app/main.py
from fastapi import FastAPI
from fastapi.security import HTTPBearer
from app.middleware.logging import log_requests
from app.controllers.auth_controller import router as auth_router
from app.controllers.user_controller import router as user_router
from app.controllers.project_controller import router as project_router
from app.controllers.issue_controller import router as issue_router
from app.controllers.comment_controller import router as comment_router
from app.controllers.contributor_controller import router as contributor_router


app = FastAPI(
    title="Issue Tracking",
    description="Ceci est une description de mon API FastAPI.",
    version="1.0.0",
    contact={
        "name": "Support Technique",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Ajoute le middleware de journalisation
app.middleware("http")(log_requests)

# Inclut les routeurs
app.include_router(auth_router, prefix="/api/auth")
app.include_router(user_router, prefix="/users")
app.include_router(project_router, prefix="/projects")
app.include_router(issue_router, prefix="/issues")
app.include_router(comment_router, prefix="/comments")
app.include_router(contributor_router, prefix="/contributors")