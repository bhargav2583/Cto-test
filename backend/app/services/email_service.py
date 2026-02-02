"""Email generation service for creating cover letters."""

import logging
from typing import Any

from .llm_provider import LLMProvider, LLMProviderError
from .prompts import ToneType, build_cover_letter_prompt, build_subject_line_prompt

logger = logging.getLogger(__name__)


class EmailGenerationError(Exception):
    """Exception raised when email generation fails."""

    pass


class EmailGenerationService:
    """Service for generating professional cover letters using LLM."""

    def __init__(self, llm_provider: LLMProvider):
        """Initialize the email generation service.

        Args:
            llm_provider: The LLM provider to use for generation
        """
        self.llm_provider = llm_provider

    async def generate_cover_letter(
        self,
        cv_text: str,
        job_title: str,
        job_description: str,
        company_name: str | None = None,
        tone: ToneType = "professional",
    ) -> dict[str, Any]:
        """Generate a professional cover letter with subject line.

        Args:
            cv_text: The full text content of the CV/resume
            job_title: The job title for the position
            job_description: The full job description
            company_name: Optional company name for personalization
            tone: Tone of the cover letter

        Returns:
            Dictionary containing:
                - subject: The email subject line
                - body: The cover letter body
                - metadata: Additional metadata about the generation

        Raises:
            EmailGenerationError: If generation fails
        """
        try:
            logger.info(f"Generating cover letter for position: {job_title}, tone: {tone}")

            # Generate the cover letter body
            body_system_prompt, body_user_prompt = build_cover_letter_prompt(
                cv_text=cv_text,
                job_title=job_title,
                job_description=job_description,
                company_name=company_name,
                tone=tone,
            )

            body_result = await self.llm_provider.generate_completion(
                prompt=body_user_prompt,
                system_prompt=body_system_prompt,
                temperature=0.7,
                max_tokens=1500,
            )

            # Generate the subject line
            subject_system_prompt, subject_user_prompt = build_subject_line_prompt(
                job_title=job_title,
                company_name=company_name,
            )

            subject_result = await self.llm_provider.generate_completion(
                prompt=subject_user_prompt,
                system_prompt=subject_system_prompt,
                temperature=0.5,
                max_tokens=100,
            )

            result = {
                "subject": subject_result["content"].strip(),
                "body": body_result["content"].strip(),
                "metadata": {
                    "model": body_result["model"],
                    "tone": tone,
                    "tokens_body": str(body_result["tokens_used"]),
                    "tokens_subject": str(subject_result["tokens_used"]),
                    "total_tokens": str(body_result["tokens_used"] + subject_result["tokens_used"]),
                },
            }

            logger.info(
                f"Cover letter generated successfully. "
                f"Total tokens: {result['metadata']['total_tokens']}"
            )

            return result

        except LLMProviderError as e:
            logger.error(f"LLM provider error during generation: {str(e)}")
            # Return fallback response
            return self._generate_fallback_response(
                job_title=job_title,
                company_name=company_name,
                error_message=str(e),
            )
        except Exception as e:
            logger.error(f"Unexpected error during email generation: {str(e)}")
            raise EmailGenerationError(f"Failed to generate cover letter: {str(e)}") from e

    def _generate_fallback_response(
        self,
        job_title: str,
        company_name: str | None = None,
        error_message: str = "",
    ) -> dict[str, Any]:
        """Generate a fallback response when LLM fails.

        Args:
            job_title: The job title for the position
            company_name: Optional company name
            error_message: The error message from the LLM provider

        Returns:
            Dictionary with fallback content
        """
        logger.warning("Using fallback response due to LLM failure")

        company_mention = f" at {company_name}" if company_name else ""
        subject = f"Application for {job_title} Position{company_mention}"

        body = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position{company_mention}. \
With my background and experience, I believe I would be a valuable addition to your team.

I am particularly drawn to this opportunity because it aligns well with my career goals \
and professional expertise. My skills and experience make me well-suited for the \
responsibilities outlined in the job description.

I would welcome the opportunity to discuss how my qualifications match your needs. \
Thank you for considering my application.

Best regards"""

        return {
            "subject": subject,
            "body": body,
            "metadata": {
                "model": "fallback",
                "tone": "professional",
                "error": error_message,
                "fallback_used": "true",
            },
        }
