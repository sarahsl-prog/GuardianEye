"""Tests for LLM factory."""

import pytest

from src.core.llm_factory import LLMFactory, LLMProvider


def test_llm_provider_enum():
    """Test LLM provider enum values."""
    assert LLMProvider.OPENAI.value == "openai"
    assert LLMProvider.ANTHROPIC.value == "anthropic"
    assert LLMProvider.GOOGLE.value == "google"
    assert LLMProvider.OLLAMA.value == "ollama"
    assert LLMProvider.LMSTUDIO.value == "lmstudio"


def test_create_llm_invalid_provider():
    """Test creating LLM with invalid provider."""
    with pytest.raises(ValueError):
        LLMFactory.create_llm(provider="invalid_provider")


# TODO: Add more comprehensive tests
# - Test creating LLM for each provider (with mocked API keys)
# - Test default LLM creation
# - Test temperature and model parameter passing
