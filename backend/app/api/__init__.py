"""API routers for the backend application."""

from fastapi import APIRouter

from .email import router as email_router
from .routes import router as health_router

router = APIRouter()
router.include_router(health_router)
router.include_router(email_router)

__all__ = ["router"]
