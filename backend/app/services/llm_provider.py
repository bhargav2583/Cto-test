"""Abstract LLM provider interface for pluggable implementations."""

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate_completion(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> dict[str, Any]:
        """Generate a completion from the LLM.

        Args:
            prompt: The user prompt to send to the LLM
            system_prompt: Optional system prompt for context
            temperature: Temperature for generation (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Dictionary containing:
                - content: The generated text
                - model: The model used
                - tokens_used: Number of tokens used (if available)
                - finish_reason: Why the generation stopped

        Raises:
            LLMProviderError: If the LLM provider fails
        """
        pass


class LLMProviderError(Exception):
    """Exception raised when LLM provider fails."""

    def __init__(self, message: str, provider: str, original_error: Exception | None = None):
        self.provider = provider
        self.original_error = original_error
        super().__init__(message)
