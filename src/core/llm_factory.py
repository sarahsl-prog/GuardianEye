"""LLM Factory for creating language model instances."""

from enum import Enum
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from src.config.settings import settings


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"


class LLMFactory:
    """Factory class for creating LLM instances based on provider."""

    @staticmethod
    def create_llm(
        provider: LLMProvider | str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        **kwargs: Any
    ) -> BaseChatModel:
        """
        Create LLM instance based on provider.

        Args:
            provider: LLM provider to use (defaults to settings.llm_provider)
            model: Model name (defaults to settings.llm_model)
            temperature: Temperature for generation (defaults to settings.llm_temperature)
            **kwargs: Additional provider-specific arguments

        Returns:
            BaseChatModel instance

        Raises:
            ValueError: If provider is unknown or required API key is missing
        """
        # Use defaults from settings if not provided
        if provider is None:
            provider = settings.llm_provider
        if model is None:
            model = settings.llm_model
        if temperature is None:
            temperature = settings.llm_temperature

        # Convert string to enum if needed
        if isinstance(provider, str):
            provider = LLMProvider(provider.lower())

        if provider == LLMProvider.OPENAI:
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            return ChatOpenAI(
                model=model or "gpt-4-turbo-preview",
                temperature=temperature,
                api_key=settings.openai_api_key,
                **kwargs
            )

        elif provider == LLMProvider.ANTHROPIC:
            if not settings.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            return ChatAnthropic(
                model=model or "claude-3-5-sonnet-20241022",
                temperature=temperature,
                api_key=settings.anthropic_api_key,
                **kwargs
            )

        elif provider == LLMProvider.GOOGLE:
            if not settings.google_api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
            return ChatGoogleGenerativeAI(
                model=model or "gemini-2.0-flash-exp",
                temperature=temperature,
                google_api_key=settings.google_api_key,
                **kwargs
            )

        elif provider == LLMProvider.OLLAMA:
            return ChatOllama(
                model=model or "llama3.1:8b",
                temperature=temperature,
                base_url=kwargs.get("base_url", settings.ollama_base_url),
                **{k: v for k, v in kwargs.items() if k != "base_url"}
            )

        elif provider == LLMProvider.LMSTUDIO:
            # LMStudio uses OpenAI-compatible API
            return ChatOpenAI(
                model=model or "local-model",
                temperature=temperature,
                base_url=kwargs.get("base_url", settings.lmstudio_base_url),
                api_key="lm-studio",  # LMStudio doesn't validate API keys
                **{k: v for k, v in kwargs.items() if k != "base_url"}
            )

        else:
            raise ValueError(f"Unknown provider: {provider}")

    @staticmethod
    def get_default_llm() -> BaseChatModel:
        """Get default LLM from settings."""
        return LLMFactory.create_llm()
