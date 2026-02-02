"""Unit tests for OpenAI provider."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai import OpenAIError

from app.services.llm_provider import LLMProviderError
from app.services.openai_provider import OpenAIProvider


class TestOpenAIProvider:
    """Test OpenAI provider implementation."""

    def test_initialization_without_api_key(self):
        """Test that provider raises error without API key."""
        with pytest.raises(ValueError, match="API key is required"):
            OpenAIProvider(api_key="")

    def test_initialization_with_api_key(self):
        """Test successful initialization with API key."""
        provider = OpenAIProvider(api_key="sk-test-key")
        assert provider.model == "gpt-3.5-turbo"

    def test_initialization_with_custom_model(self):
        """Test initialization with custom model."""
        provider = OpenAIProvider(api_key="sk-test-key", model="gpt-4")
        assert provider.model == "gpt-4"

    @pytest.mark.asyncio
    async def test_generate_completion_success(self):
        """Test successful completion generation."""
        provider = OpenAIProvider(api_key="sk-test-key")

        # Mock the OpenAI client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(content="Generated text"),
                finish_reason="stop",
            )
        ]
        mock_response.model = "gpt-3.5-turbo"
        mock_response.usage = MagicMock(total_tokens=100)

        with patch.object(
            provider.client.chat.completions,
            "create",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            result = await provider.generate_completion(
                prompt="Test prompt",
                system_prompt="System prompt",
            )

            assert result["content"] == "Generated text"
            assert result["model"] == "gpt-3.5-turbo"
            assert result["tokens_used"] == 100
            assert result["finish_reason"] == "stop"

    @pytest.mark.asyncio
    async def test_generate_completion_without_system_prompt(self):
        """Test completion generation without system prompt."""
        provider = OpenAIProvider(api_key="sk-test-key")

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(content="Response"),
                finish_reason="stop",
            )
        ]
        mock_response.model = "gpt-3.5-turbo"
        mock_response.usage = MagicMock(total_tokens=50)

        with patch.object(
            provider.client.chat.completions,
            "create",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_create:
            await provider.generate_completion(prompt="Test prompt")

            # Verify only user message was sent
            call_args = mock_create.call_args
            messages = call_args.kwargs["messages"]
            assert len(messages) == 1
            assert messages[0]["role"] == "user"

    @pytest.mark.asyncio
    async def test_generate_completion_with_custom_params(self):
        """Test completion with custom temperature and max_tokens."""
        provider = OpenAIProvider(api_key="sk-test-key")

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(content="Response"),
                finish_reason="stop",
            )
        ]
        mock_response.model = "gpt-3.5-turbo"
        mock_response.usage = MagicMock(total_tokens=50)

        with patch.object(
            provider.client.chat.completions,
            "create",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_create:
            await provider.generate_completion(
                prompt="Test",
                temperature=0.9,
                max_tokens=2000,
            )

            call_args = mock_create.call_args
            assert call_args.kwargs["temperature"] == 0.9
            assert call_args.kwargs["max_tokens"] == 2000

    @pytest.mark.asyncio
    async def test_generate_completion_openai_error(self):
        """Test handling of OpenAI API errors."""
        provider = OpenAIProvider(api_key="sk-test-key")

        with patch.object(
            provider.client.chat.completions,
            "create",
            new_callable=AsyncMock,
            side_effect=OpenAIError("API Error"),
        ):
            with pytest.raises(LLMProviderError) as exc_info:
                await provider.generate_completion(prompt="Test")

            assert exc_info.value.provider == "openai"
            assert "Failed to generate completion" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_completion_unexpected_error(self):
        """Test handling of unexpected errors."""
        provider = OpenAIProvider(api_key="sk-test-key")

        with patch.object(
            provider.client.chat.completions,
            "create",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Unexpected error"),
        ):
            with pytest.raises(LLMProviderError) as exc_info:
                await provider.generate_completion(prompt="Test")

            assert exc_info.value.provider == "openai"
            assert "Unexpected error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_completion_empty_content(self):
        """Test handling when API returns empty content."""
        provider = OpenAIProvider(api_key="sk-test-key")

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(content=None),
                finish_reason="stop",
            )
        ]
        mock_response.model = "gpt-3.5-turbo"
        mock_response.usage = MagicMock(total_tokens=10)

        with patch.object(
            provider.client.chat.completions,
            "create",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            result = await provider.generate_completion(prompt="Test")

            # Should return empty string when content is None
            assert result["content"] == ""

    @pytest.mark.asyncio
    async def test_generate_completion_no_usage_info(self):
        """Test handling when API doesn't return usage information."""
        provider = OpenAIProvider(api_key="sk-test-key")

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(content="Response"),
                finish_reason="stop",
            )
        ]
        mock_response.model = "gpt-3.5-turbo"
        mock_response.usage = None

        with patch.object(
            provider.client.chat.completions,
            "create",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            result = await provider.generate_completion(prompt="Test")

            # Should default to 0 when usage is not available
            assert result["tokens_used"] == 0
