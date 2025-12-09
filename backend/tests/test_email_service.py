"""Unit tests for email generation service."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.email_service import EmailGenerationService
from app.services.llm_provider import LLMProviderError
from app.services.prompts import build_cover_letter_prompt, build_subject_line_prompt


class TestPromptBuilding:
    """Test prompt assembly and personalization logic."""

    def test_build_cover_letter_prompt_basic(self):
        """Test basic cover letter prompt building."""
        cv_text = "Software engineer with 5 years experience"
        job_title = "Senior Developer"
        job_description = "Looking for an experienced developer"

        system_prompt, user_prompt = build_cover_letter_prompt(
            cv_text=cv_text,
            job_title=job_title,
            job_description=job_description,
        )

        assert "career advisor" in system_prompt.lower()
        assert cv_text in user_prompt
        assert job_title in user_prompt
        assert job_description in user_prompt

    def test_build_cover_letter_prompt_with_company(self):
        """Test cover letter prompt with company name."""
        cv_text = "Data scientist"
        job_title = "ML Engineer"
        job_description = "Build ML models"
        company_name = "TechCorp"

        system_prompt, user_prompt = build_cover_letter_prompt(
            cv_text=cv_text,
            job_title=job_title,
            job_description=job_description,
            company_name=company_name,
        )

        assert company_name in user_prompt
        assert "at TechCorp" in user_prompt

    def test_build_cover_letter_prompt_different_tones(self):
        """Test that different tones produce different system prompts."""
        cv_text = "Engineer"
        job_title = "Developer"
        job_description = "Build apps"

        professional_system, _ = build_cover_letter_prompt(
            cv_text=cv_text,
            job_title=job_title,
            job_description=job_description,
            tone="professional",
        )

        enthusiastic_system, _ = build_cover_letter_prompt(
            cv_text=cv_text,
            job_title=job_title,
            job_description=job_description,
            tone="enthusiastic",
        )

        formal_system, _ = build_cover_letter_prompt(
            cv_text=cv_text,
            job_title=job_title,
            job_description=job_description,
            tone="formal",
        )

        # Each tone should produce a different system prompt
        assert professional_system != enthusiastic_system
        assert enthusiastic_system != formal_system
        assert professional_system != formal_system

    def test_build_subject_line_prompt_basic(self):
        """Test basic subject line prompt building."""
        job_title = "Software Engineer"

        system_prompt, user_prompt = build_subject_line_prompt(job_title=job_title)

        assert "subject line" in system_prompt.lower()
        assert job_title in user_prompt

    def test_build_subject_line_prompt_with_company(self):
        """Test subject line prompt with company name."""
        job_title = "Product Manager"
        company_name = "StartupXYZ"

        system_prompt, user_prompt = build_subject_line_prompt(
            job_title=job_title, company_name=company_name
        )

        assert company_name in user_prompt
        assert job_title in user_prompt


class TestEmailGenerationService:
    """Test email generation service with mocked LLM."""

    @pytest.fixture
    def mock_llm_provider(self):
        """Create a mock LLM provider."""
        provider = MagicMock()
        provider.generate_completion = AsyncMock()
        return provider

    @pytest.fixture
    def service(self, mock_llm_provider):
        """Create an email generation service with mocked provider."""
        return EmailGenerationService(mock_llm_provider)

    @pytest.mark.asyncio
    async def test_generate_cover_letter_success(self, service, mock_llm_provider):
        """Test successful cover letter generation."""
        # Mock LLM responses
        mock_llm_provider.generate_completion.side_effect = [
            # First call for body
            {
                "content": "Dear Hiring Manager, I am excited to apply...",
                "model": "gpt-3.5-turbo",
                "tokens_used": 300,
                "finish_reason": "stop",
            },
            # Second call for subject
            {
                "content": "Application for Senior Developer Position",
                "model": "gpt-3.5-turbo",
                "tokens_used": 20,
                "finish_reason": "stop",
            },
        ]

        result = await service.generate_cover_letter(
            cv_text="Software engineer with 5 years experience",
            job_title="Senior Developer",
            job_description="Looking for an experienced developer",
        )

        assert "subject" in result
        assert "body" in result
        assert "metadata" in result
        assert result["subject"] == "Application for Senior Developer Position"
        assert "Dear Hiring Manager" in result["body"]
        assert result["metadata"]["model"] == "gpt-3.5-turbo"
        assert result["metadata"]["total_tokens"] == "320"

    @pytest.mark.asyncio
    async def test_generate_cover_letter_with_company(self, service, mock_llm_provider):
        """Test cover letter generation with company name."""
        mock_llm_provider.generate_completion.side_effect = [
            {
                "content": "Dear Hiring Manager at TechCorp...",
                "model": "gpt-3.5-turbo",
                "tokens_used": 350,
                "finish_reason": "stop",
            },
            {
                "content": "Application for ML Engineer at TechCorp",
                "model": "gpt-3.5-turbo",
                "tokens_used": 25,
                "finish_reason": "stop",
            },
        ]

        result = await service.generate_cover_letter(
            cv_text="Data scientist",
            job_title="ML Engineer",
            job_description="Build ML models",
            company_name="TechCorp",
        )

        assert "TechCorp" in result["subject"]
        # Verify the provider was called with prompts containing company name
        assert mock_llm_provider.generate_completion.call_count == 2

    @pytest.mark.asyncio
    async def test_generate_cover_letter_different_tones(self, service, mock_llm_provider):
        """Test that different tones are passed through correctly."""
        mock_llm_provider.generate_completion.side_effect = [
            {
                "content": "Enthusiastic cover letter body",
                "model": "gpt-3.5-turbo",
                "tokens_used": 300,
                "finish_reason": "stop",
            },
            {
                "content": "Enthusiastic subject",
                "model": "gpt-3.5-turbo",
                "tokens_used": 20,
                "finish_reason": "stop",
            },
        ]

        result = await service.generate_cover_letter(
            cv_text="Engineer",
            job_title="Developer",
            job_description="Build apps",
            tone="enthusiastic",
        )

        assert result["metadata"]["tone"] == "enthusiastic"

    @pytest.mark.asyncio
    async def test_generate_cover_letter_llm_failure_fallback(self, service, mock_llm_provider):
        """Test that service uses fallback when LLM fails."""
        # Mock LLM to raise an error
        mock_llm_provider.generate_completion.side_effect = LLMProviderError(
            message="API key invalid",
            provider="openai",
        )

        result = await service.generate_cover_letter(
            cv_text="Software engineer",
            job_title="Backend Developer",
            job_description="Build REST APIs",
            company_name="TestCorp",
        )

        # Should return fallback response
        assert "subject" in result
        assert "body" in result
        assert "Backend Developer" in result["subject"]
        assert "TestCorp" in result["subject"]
        assert "Dear Hiring Manager" in result["body"]
        assert result["metadata"]["model"] == "fallback"
        assert result["metadata"]["fallback_used"] == "true"

    @pytest.mark.asyncio
    async def test_generate_cover_letter_partial_failure(self, service, mock_llm_provider):
        """Test handling when first call succeeds but second fails."""
        # First call succeeds, second fails
        mock_llm_provider.generate_completion.side_effect = [
            {
                "content": "Cover letter body",
                "model": "gpt-3.5-turbo",
                "tokens_used": 300,
                "finish_reason": "stop",
            },
            LLMProviderError(
                message="Rate limit exceeded",
                provider="openai",
            ),
        ]

        result = await service.generate_cover_letter(
            cv_text="Engineer",
            job_title="Developer",
            job_description="Build apps",
        )

        # Should use fallback
        assert result["metadata"]["model"] == "fallback"

    @pytest.mark.asyncio
    async def test_fallback_response_structure(self, service):
        """Test that fallback response has correct structure."""
        fallback = service._generate_fallback_response(
            job_title="Software Engineer",
            company_name="TestCompany",
            error_message="Test error",
        )

        assert "subject" in fallback
        assert "body" in fallback
        assert "metadata" in fallback
        assert "Software Engineer" in fallback["subject"]
        assert "TestCompany" in fallback["subject"]
        assert "Dear Hiring Manager" in fallback["body"]
        assert fallback["metadata"]["model"] == "fallback"
        assert fallback["metadata"]["fallback_used"] == "true"
        assert "Test error" in fallback["metadata"]["error"]

    @pytest.mark.asyncio
    async def test_llm_provider_called_with_correct_params(self, service, mock_llm_provider):
        """Test that LLM provider is called with correct parameters."""
        mock_llm_provider.generate_completion.side_effect = [
            {
                "content": "Body",
                "model": "gpt-3.5-turbo",
                "tokens_used": 300,
                "finish_reason": "stop",
            },
            {
                "content": "Subject",
                "model": "gpt-3.5-turbo",
                "tokens_used": 20,
                "finish_reason": "stop",
            },
        ]

        await service.generate_cover_letter(
            cv_text="CV text",
            job_title="Developer",
            job_description="Job desc",
        )

        # Check first call (body generation)
        first_call = mock_llm_provider.generate_completion.call_args_list[0]
        assert first_call.kwargs["temperature"] == 0.7
        assert first_call.kwargs["max_tokens"] == 1500

        # Check second call (subject generation)
        second_call = mock_llm_provider.generate_completion.call_args_list[1]
        assert second_call.kwargs["temperature"] == 0.5
        assert second_call.kwargs["max_tokens"] == 100
