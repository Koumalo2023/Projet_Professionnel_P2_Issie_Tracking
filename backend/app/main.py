# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from app.middleware.logging import log_requests
from app.middleware.exception_handler import global_exception_handler
from app.middleware.authorization_middleware import authorization_middleware
from app.middleware.token_refresh_middleware import token_refresh_middleware
from app.utils.logger import setup_logging
from app.controllers.auth_controller import router as auth_router
from app.controllers.user_controller import router as user_router
from app.controllers.project_controller import router as project_router
from app.controllers.issue_controller import router as issue_router
from app.controllers.comment_controller import router as comment_router
from app.controllers.contributor_controller import router as contributor_router
from app.controllers.mfa_controller import router as mfa_router
from app.controllers.oauth_controller import router as oauth_router
from app.controllers.session_controller import router as session_router
from app.controllers.token_controller import router as token_router
from app.controllers.user_profile_controller import router as user_profile_router

# Configuration du logging
setup_logging()

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

# Ajoute le middleware d'autorisation RBAC
app.middleware("http")(authorization_middleware)

# Ajoute le middleware de rafraîchissement automatique des tokens
app.middleware("http")(token_refresh_middleware)

# Ajoute le gestionnaire d'exceptions global
app.add_exception_handler(Exception, global_exception_handler)

# Gestionnaire d'exceptions pour les erreurs de validation Pydantic
@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    from app.middleware.exception_handler import global_exception_handler
    return await global_exception_handler(request, exc)

# Route de santé
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Issue Tracking API",
        "version": "1.0.0"
    }

# Inclut les routeurs
app.include_router(auth_router, prefix="/api/auth")
app.include_router(user_router, prefix="/users")
app.include_router(project_router, prefix="/projects")
app.include_router(issue_router, prefix="/issues")
app.include_router(comment_router, prefix="/comments")
app.include_router(contributor_router, prefix="/contributors")
app.include_router(mfa_router, prefix="/api")
app.include_router(oauth_router, prefix="/api")
app.include_router(session_router, prefix="/api")
app.include_router(token_router, prefix="/api")
app.include_router(user_profile_router, prefix="/api")