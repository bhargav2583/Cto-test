"""Application API routes."""

from fastapi import APIRouter

from ..core.config import get_settings

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Application health check")
async def health_check() -> dict[str, str]:
    """Simple endpoint that reports the application's health."""
    settings = get_settings()
    return {
        "status": "ok",
        "environment": settings.environment,
        "app": settings.app_name,
    }
