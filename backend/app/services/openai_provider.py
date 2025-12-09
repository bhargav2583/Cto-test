"""OpenAI LLM provider implementation."""

import logging
from typing import Any

from openai import AsyncOpenAI, OpenAIError

from .llm_provider import LLMProvider, LLMProviderError

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of the LLM provider interface."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """Initialize the OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-3.5-turbo)
        """
        if not api_key:
            raise ValueError("OpenAI API key is required")

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate_completion(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> dict[str, Any]:
        """Generate a completion using OpenAI's API.

        Args:
            prompt: The user prompt to send to the LLM
            system_prompt: Optional system prompt for context
            temperature: Temperature for generation (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Dictionary containing:
                - content: The generated text
                - model: The model used
                - tokens_used: Number of tokens used
                - finish_reason: Why the generation stopped

        Raises:
            LLMProviderError: If the OpenAI API fails
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            logger.info(f"Generating completion with model {self.model}")

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            choice = response.choices[0]
            content = choice.message.content or ""

            result = {
                "content": content,
                "model": response.model,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "finish_reason": choice.finish_reason,
            }

            logger.info(
                f"Completion generated successfully. "
                f"Tokens used: {result['tokens_used']}, "
                f"Finish reason: {result['finish_reason']}"
            )

            return result

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise LLMProviderError(
                message=f"Failed to generate completion: {str(e)}",
                provider="openai",
                original_error=e,
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI provider: {str(e)}")
            raise LLMProviderError(
                message=f"Unexpected error: {str(e)}",
                provider="openai",
                original_error=e,
            ) from e
