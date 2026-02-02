"""Prompt templates for email generation."""

from typing import Literal

ToneType = Literal["professional", "enthusiastic", "formal"]


SYSTEM_PROMPTS = {
    "professional": (
        "You are an expert career advisor and professional writer specializing in "
        "crafting compelling cover letters. Your task is to create professional, "
        "well-structured cover letters that highlight relevant experience and skills "
        "while maintaining a confident and competent tone."
    ),
    "enthusiastic": (
        "You are an expert career advisor and professional writer specializing in "
        "crafting compelling cover letters. Your task is to create engaging, "
        "enthusiastic cover letters that showcase genuine interest and passion for "
        "the role while maintaining professionalism."
    ),
    "formal": (
        "You are an expert career advisor and professional writer specializing in "
        "crafting compelling cover letters. Your task is to create highly formal, "
        "traditionally-structured cover letters that emphasize qualifications and "
        "experience with appropriate business etiquette."
    ),
}


def build_cover_letter_prompt(
    cv_text: str,
    job_title: str,
    job_description: str,
    company_name: str | None = None,
    tone: ToneType = "professional",
) -> tuple[str, str]:
    """Build the prompt for cover letter generation.

    Args:
        cv_text: The full text content of the CV/resume
        job_title: The job title for the position
        job_description: The full job description
        company_name: Optional company name for personalization
        tone: Tone of the cover letter

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system_prompt = SYSTEM_PROMPTS.get(tone, SYSTEM_PROMPTS["professional"])

    company_mention = f" at {company_name}" if company_name else ""

    user_prompt = f"""Based on the following CV and job description, create a compelling \
cover letter for the position of {job_title}{company_mention}.

CV:
{cv_text}

Job Description:
{job_description}

Requirements:
1. Write a professional cover letter that highlights the most relevant experience \
and skills from the CV
2. Align the candidate's qualifications with the specific requirements mentioned \
in the job description
3. Keep the tone {tone} throughout
4. Structure the letter with clear paragraphs (introduction, body highlighting \
qualifications, conclusion)
5. Make it compelling but honest - don't exaggerate or add false information
6. Keep it concise (300-400 words)
7. Do not include placeholder fields like [Your Name], [Date], etc. - write a \
complete, ready-to-send letter

Generate only the body of the cover letter, without subject line, salutation \
addresses, or signature blocks."""

    return system_prompt, user_prompt


def build_subject_line_prompt(
    job_title: str,
    company_name: str | None = None,
) -> tuple[str, str]:
    """Build the prompt for email subject line generation.

    Args:
        job_title: The job title for the position
        company_name: Optional company name for personalization

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system_prompt = (
        "You are an expert at crafting professional email subject lines for job applications."
    )

    company_mention = f" at {company_name}" if company_name else ""

    user_prompt = f"""Create a professional, clear email subject line for a job \
application for the position of {job_title}{company_mention}.

Requirements:
1. Be clear and specific about the position
2. Include the job title
3. Keep it concise (under 60 characters if possible)
4. Make it professional and attention-grabbing
5. Include company name if provided

Generate only the subject line text, without quotes or extra formatting."""

    return system_prompt, user_prompt
