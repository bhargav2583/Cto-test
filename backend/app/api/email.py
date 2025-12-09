"""Email generation API endpoints."""

import logging

from fastapi import APIRouter, HTTPException, status

from ..core.config import get_settings
from ..services.email_service import EmailGenerationError, EmailGenerationService
from ..services.openai_provider import OpenAIProvider
from .schemas.email import EmailPreviewRequest, EmailPreviewResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email", tags=["Email Generation"])


def get_email_service() -> EmailGenerationService:
    """Get an instance of the email generation service.

    Returns:
        EmailGenerationService instance configured with OpenAI provider

    Raises:
        HTTPException: If OpenAI API key is not configured
    """
    settings = get_settings()

    if not settings.openai_api_key:
        logger.error("OpenAI API key not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Email generation service is not configured. "
                "Please set OPENAI_API_KEY environment variable."
            ),
        )

    try:
        llm_provider = OpenAIProvider(
            api_key=settings.openai_api_key,
            model="gpt-3.5-turbo",
        )
        return EmailGenerationService(llm_provider)
    except ValueError as e:
        logger.error(f"Failed to initialize email service: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to initialize email generation service: {str(e)}",
        ) from e


@router.post(
    "/preview",
    response_model=EmailPreviewResponse,
    summary="Generate cover letter preview",
    description="""
    Generate a professional cover letter preview based on CV and job details.
    
    This endpoint uses AI to create a personalized cover letter that:
    - Highlights relevant experience from the CV
    - Aligns qualifications with job requirements
    - Maintains the specified tone
    - Generates an appropriate email subject line
    
    If the AI service fails, a fallback template will be used to ensure
    the endpoint always returns a usable response.
    """,
    responses={
        200: {
            "description": "Successfully generated cover letter",
            "content": {
                "application/json": {
                    "example": {
                        "subject": (
                            "Application for Senior Software Engineer " "Position at TechCorp"
                        ),
                        "body": (
                            "Dear Hiring Manager,\n\n"
                            "I am writing to express my strong interest..."
                        ),
                        "metadata": {
                            "model": "gpt-3.5-turbo",
                            "tone": "professional",
                            "total_tokens": "450",
                        },
                    }
                }
            },
        },
        400: {
            "description": "Invalid request parameters",
        },
        503: {
            "description": "Service unavailable (API key not configured)",
        },
    },
)
async def preview_email(request: EmailPreviewRequest) -> EmailPreviewResponse:
    """Generate a cover letter preview.

    Args:
        request: Email preview request containing CV and job details

    Returns:
        EmailPreviewResponse with generated subject and body

    Raises:
        HTTPException: If the service is unavailable or generation fails
    """
    try:
        service = get_email_service()

        result = await service.generate_cover_letter(
            cv_text=request.cv_text,
            job_title=request.job_title,
            job_description=request.job_description,
            company_name=request.company_name,
            tone=request.tone or "professional",
        )

        return EmailPreviewResponse(
            subject=result["subject"],
            body=result["body"],
            metadata=result["metadata"],
        )

    except HTTPException:
        # Re-raise HTTPExceptions (e.g., from get_email_service) without wrapping
        raise
    except EmailGenerationError as e:
        logger.error(f"Email generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate email preview: {str(e)}",
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in email preview endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating the email preview.",
        ) from e
