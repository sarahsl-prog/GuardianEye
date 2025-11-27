"""Tests for LLM factory."""

import pytest
from unittest.mock import patch, MagicMock

from src.core.llm_factory import LLMFactory, LLMProvider
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI


def test_llm_provider_enum():
    """Test LLM provider enum values."""
    assert LLMProvider.OPENAI.value == "openai"
    assert LLMProvider.ANTHROPIC.value == "anthropic"
    assert LLMProvider.GOOGLE.value == "google"
    assert LLMProvider.OLLAMA.value == "ollama"
    assert LLMProvider.LMSTUDIO.value == "lmstudio"


def test_create_llm_invalid_provider():
    """Test creating LLM with invalid provider."""
    with pytest.raises(ValueError, match="Unknown provider"):
        LLMFactory.create_llm(provider="invalid_provider")


@patch("src.core.llm_factory.settings")
@patch("src.core.llm_factory.ChatOpenAI")
def test_create_openai_llm(mock_openai_class, mock_settings):
    """Test creating OpenAI LLM."""
    # Setup mocks
    mock_settings.openai_api_key = "test-openai-key"
    mock_llm = MagicMock()
    mock_openai_class.return_value = mock_llm

    # Create LLM
    llm = LLMFactory.create_llm(
        provider=LLMProvider.OPENAI,
        model="gpt-4",
        temperature=0.5
    )

    # Verify
    assert llm == mock_llm
    mock_openai_class.assert_called_once_with(
        model="gpt-4",
        temperature=0.5,
        api_key="test-openai-key"
    )


@patch("src.core.llm_factory.settings")
def test_create_openai_llm_missing_api_key(mock_settings):
    """Test creating OpenAI LLM without API key raises error."""
    mock_settings.openai_api_key = None

    with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
        LLMFactory.create_llm(provider=LLMProvider.OPENAI)


@patch("src.core.llm_factory.settings")
@patch("src.core.llm_factory.ChatAnthropic")
def test_create_anthropic_llm(mock_anthropic_class, mock_settings):
    """Test creating Anthropic LLM."""
    # Setup mocks
    mock_settings.anthropic_api_key = "test-anthropic-key"
    mock_llm = MagicMock()
    mock_anthropic_class.return_value = mock_llm

    # Create LLM
    llm = LLMFactory.create_llm(
        provider=LLMProvider.ANTHROPIC,
        model="claude-3-5-sonnet-20241022",
        temperature=0.7
    )

    # Verify
    assert llm == mock_llm
    mock_anthropic_class.assert_called_once_with(
        model="claude-3-5-sonnet-20241022",
        temperature=0.7,
        api_key="test-anthropic-key"
    )


@patch("src.core.llm_factory.settings")
def test_create_anthropic_llm_missing_api_key(mock_settings):
    """Test creating Anthropic LLM without API key raises error."""
    mock_settings.anthropic_api_key = None

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY not found"):
        LLMFactory.create_llm(provider=LLMProvider.ANTHROPIC)


@patch("src.core.llm_factory.settings")
@patch("src.core.llm_factory.ChatGoogleGenerativeAI")
def test_create_google_llm(mock_google_class, mock_settings):
    """Test creating Google LLM."""
    # Setup mocks
    mock_settings.google_api_key = "test-google-key"
    mock_llm = MagicMock()
    mock_google_class.return_value = mock_llm

    # Create LLM
    llm = LLMFactory.create_llm(
        provider=LLMProvider.GOOGLE,
        model="gemini-2.0-flash-exp",
        temperature=0.8
    )

    # Verify
    assert llm == mock_llm
    mock_google_class.assert_called_once_with(
        model="gemini-2.0-flash-exp",
        temperature=0.8,
        google_api_key="test-google-key"
    )


@patch("src.core.llm_factory.settings")
def test_create_google_llm_missing_api_key(mock_settings):
    """Test creating Google LLM without API key raises error."""
    mock_settings.google_api_key = None

    with pytest.raises(ValueError, match="GOOGLE_API_KEY not found"):
        LLMFactory.create_llm(provider=LLMProvider.GOOGLE)


@patch("src.core.llm_factory.settings")
@patch("src.core.llm_factory.ChatOllama")
def test_create_ollama_llm(mock_ollama_class, mock_settings):
    """Test creating Ollama LLM."""
    # Setup mocks
    mock_settings.ollama_base_url = "http://localhost:11434"
    mock_llm = MagicMock()
    mock_ollama_class.return_value = mock_llm

    # Create LLM
    llm = LLMFactory.create_llm(
        provider=LLMProvider.OLLAMA,
        model="llama3.1:8b",
        temperature=0.9
    )

    # Verify
    assert llm == mock_llm
    mock_ollama_class.assert_called_once_with(
        model="llama3.1:8b",
        temperature=0.9,
        base_url="http://localhost:11434"
    )


@patch("src.core.llm_factory.settings")
@patch("src.core.llm_factory.ChatOllama")
def test_create_ollama_llm_custom_base_url(mock_ollama_class, mock_settings):
    """Test creating Ollama LLM with custom base URL."""
    mock_settings.ollama_base_url = "http://localhost:11434"
    mock_llm = MagicMock()
    mock_ollama_class.return_value = mock_llm

    # Create LLM with custom base_url
    llm = LLMFactory.create_llm(
        provider=LLMProvider.OLLAMA,
        model="llama3.1:8b",
        temperature=0.7,
        base_url="http://custom-ollama:11434"
    )

    # Verify custom base_url is used
    assert llm == mock_llm
    mock_ollama_class.assert_called_once_with(
        model="llama3.1:8b",
        temperature=0.7,
        base_url="http://custom-ollama:11434"
    )


@patch("src.core.llm_factory.settings")
@patch("src.core.llm_factory.ChatOpenAI")
def test_create_lmstudio_llm(mock_openai_class, mock_settings):
    """Test creating LMStudio LLM (uses OpenAI-compatible API)."""
    # Setup mocks
    mock_settings.lmstudio_base_url = "http://localhost:1234/v1"
    mock_llm = MagicMock()
    mock_openai_class.return_value = mock_llm

    # Create LLM
    llm = LLMFactory.create_llm(
        provider=LLMProvider.LMSTUDIO,
        model="local-model",
        temperature=0.6
    )

    # Verify
    assert llm == mock_llm
    mock_openai_class.assert_called_once_with(
        model="local-model",
        temperature=0.6,
        base_url="http://localhost:1234/v1",
        api_key="lm-studio"  # LMStudio doesn't validate API keys
    )


@patch("src.core.llm_factory.settings")
@patch("src.core.llm_factory.ChatOllama")
def test_get_default_llm(mock_ollama_class, mock_settings):
    """Test getting default LLM from settings."""
    # Setup mocks
    mock_settings.llm_provider = "ollama"
    mock_settings.llm_model = "llama3.1:8b"
    mock_settings.llm_temperature = 0.7
    mock_settings.ollama_base_url = "http://localhost:11434"
    mock_llm = MagicMock()
    mock_ollama_class.return_value = mock_llm

    # Get default LLM
    llm = LLMFactory.get_default_llm()

    # Verify
    assert llm == mock_llm
    mock_ollama_class.assert_called_once_with(
        model="llama3.1:8b",
        temperature=0.7,
        base_url="http://localhost:11434"
    )


@patch("src.core.llm_factory.settings")
@patch("src.core.llm_factory.ChatOpenAI")
def test_create_llm_with_string_provider(mock_openai_class, mock_settings):
    """Test creating LLM with string provider instead of enum."""
    # Setup mocks
    mock_settings.openai_api_key = "test-key"
    mock_llm = MagicMock()
    mock_openai_class.return_value = mock_llm

    # Create LLM with string provider
    llm = LLMFactory.create_llm(
        provider="openai",  # String instead of enum
        model="gpt-4",
        temperature=0.5
    )

    # Verify it works
    assert llm == mock_llm


@patch("src.core.llm_factory.settings")
@patch("src.core.llm_factory.ChatOllama")
def test_create_llm_with_defaults(mock_ollama_class, mock_settings):
    """Test creating LLM uses settings defaults when not specified."""
    # Setup mocks
    mock_settings.llm_provider = "ollama"
    mock_settings.llm_model = "default-model"
    mock_settings.llm_temperature = 0.75
    mock_settings.ollama_base_url = "http://localhost:11434"
    mock_llm = MagicMock()
    mock_ollama_class.return_value = mock_llm

    # Create LLM without specifying provider/model/temp
    llm = LLMFactory.create_llm()

    # Verify defaults from settings are used
    assert llm == mock_llm
    mock_ollama_class.assert_called_once_with(
        model="default-model",
        temperature=0.75,
        base_url="http://localhost:11434"
    )


@patch("src.core.llm_factory.settings")
@patch("src.core.llm_factory.ChatOpenAI")
def test_create_llm_with_extra_kwargs(mock_openai_class, mock_settings):
    """Test creating LLM with additional kwargs."""
    # Setup mocks
    mock_settings.openai_api_key = "test-key"
    mock_llm = MagicMock()
    mock_openai_class.return_value = mock_llm

    # Create LLM with extra kwargs
    llm = LLMFactory.create_llm(
        provider=LLMProvider.OPENAI,
        model="gpt-4",
        temperature=0.5,
        max_tokens=1000,
        top_p=0.9
    )

    # Verify extra kwargs are passed through
    assert llm == mock_llm
    mock_openai_class.assert_called_once_with(
        model="gpt-4",
        temperature=0.5,
        api_key="test-key",
        max_tokens=1000,
        top_p=0.9
    )


def test_llm_provider_enum_from_string():
    """Test converting string to LLMProvider enum."""
    assert LLMProvider("openai") == LLMProvider.OPENAI
    assert LLMProvider("anthropic") == LLMProvider.ANTHROPIC
    assert LLMProvider("google") == LLMProvider.GOOGLE
    assert LLMProvider("ollama") == LLMProvider.OLLAMA
    assert LLMProvider("lmstudio") == LLMProvider.LMSTUDIO

    with pytest.raises(ValueError):
        LLMProvider("invalid")
