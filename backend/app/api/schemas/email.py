"""Email generation API schemas."""

from pydantic import BaseModel, Field


class EmailPreviewRequest(BaseModel):
    """Request schema for email preview generation."""

    cv_text: str = Field(
        ...,
        description="The full text content of the CV/resume",
        min_length=1,
    )
    job_title: str = Field(
        ...,
        description="The job title for the position being applied to",
        min_length=1,
    )
    job_description: str = Field(
        ...,
        description="The full job description text",
        min_length=1,
    )
    company_name: str | None = Field(
        default=None,
        description="Optional company name for personalization",
    )
    tone: str | None = Field(
        default="professional",
        description="Tone of the cover letter (professional, enthusiastic, formal)",
    )


class EmailPreviewResponse(BaseModel):
    """Response schema for email preview generation."""

    subject: str = Field(
        ...,
        description="Generated email subject line",
    )
    body: str = Field(
        ...,
        description="Generated cover letter body",
    )
    metadata: dict[str, str] = Field(
        default_factory=dict,
        description="Additional metadata about the generation (model, tokens, etc.)",
    )
