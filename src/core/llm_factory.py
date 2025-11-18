"""LLM provider factory pattern for multi-provider support."""

from enum import Enum
from typing import Any
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

from src.config.settings import settings


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"


class LLMFactory:
    """Factory for creating LLM instances based on provider."""

    @staticmethod
    def create_llm(
        provider: str | LLMProvider | None = None,
        model: str | None = None,
        temperature: float | None = None,
        **kwargs: Any
    ) -> BaseChatModel:
        """Create LLM instance based on provider.

        Args:
            provider: LLM provider (defaults to settings.llm_provider)
            model: Model name (defaults to settings.llm_model)
            temperature: Temperature for generation (defaults to settings.llm_temperature)
            **kwargs: Additional provider-specific arguments

        Returns:
            BaseChatModel instance

        Raises:
            ValueError: If provider is unknown
        """
        # Use defaults from settings
        provider = provider or settings.llm_provider
        model = model or settings.llm_model
        temperature = temperature if temperature is not None else settings.llm_temperature

        # Convert to enum if string
        if isinstance(provider, str):
            provider = LLMProvider(provider.lower())

        if provider == LLMProvider.OPENAI:
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=settings.openai_api_key,
                **kwargs
            )

        elif provider == LLMProvider.ANTHROPIC:
            return ChatAnthropic(
                model=model,
                temperature=temperature,
                api_key=settings.anthropic_api_key,
                **kwargs
            )

        elif provider == LLMProvider.GOOGLE:
            return ChatGoogleGenerativeAI(
                model=model,
                temperature=temperature,
                google_api_key=settings.google_api_key,
                **kwargs
            )

        elif provider == LLMProvider.OLLAMA:
            return ChatOllama(
                model=model,
                temperature=temperature,
                base_url=kwargs.get("base_url", settings.ollama_base_url),
                **kwargs
            )

        elif provider == LLMProvider.LMSTUDIO:
            # LMStudio uses OpenAI-compatible API
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                base_url=kwargs.get("base_url", settings.lmstudio_base_url),
                api_key="lm-studio",  # LMStudio doesn't validate
                **kwargs
            )

        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

    @staticmethod
    def create_default_llm(**kwargs: Any) -> BaseChatModel:
        """Create LLM using default settings.

        Args:
            **kwargs: Additional provider-specific arguments

        Returns:
            BaseChatModel instance with default configuration
        """
        return LLMFactory.create_llm(**kwargs)
