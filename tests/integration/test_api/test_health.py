"""Health endpoint integration tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"


def test_api_v1_health_endpoint(client):
    """Test API v1 health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_liveness_endpoint(client):
    """Test liveness check endpoint."""
    response = client.get("/api/v1/live")
    assert response.status_code == 200
    data = response.json()
    assert data["alive"] is True


@patch("src.api.v1.health.get_postgres_connection")
@patch("src.api.v1.health.get_redis_client")
@patch("src.api.v1.health.LLMFactory.get_default_llm")
def test_readiness_endpoint_all_healthy(mock_llm, mock_redis, mock_postgres, client):
    """Test readiness check when all services are healthy."""
    # Mock PostgreSQL connection
    mock_conn = AsyncMock()
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__aenter__.return_value = mock_conn
    mock_postgres.return_value = mock_engine

    # Mock Redis client
    mock_redis_client = AsyncMock()
    mock_redis_client.ping = AsyncMock()
    mock_redis.return_value = mock_redis_client

    # Mock LLM
    mock_llm.return_value = MagicMock()

    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True
    assert data["services"]["postgres"] == "healthy"
    assert data["services"]["redis"] == "healthy"
    assert data["services"]["llm"] == "healthy"


@patch("src.api.v1.health.get_postgres_connection")
@patch("src.api.v1.health.get_redis_client")
@patch("src.api.v1.health.LLMFactory.get_default_llm")
def test_readiness_endpoint_postgres_unhealthy(mock_llm, mock_redis, mock_postgres, client):
    """Test readiness check when PostgreSQL is unhealthy."""
    # Mock PostgreSQL connection failure
    mock_postgres.side_effect = Exception("Connection failed")

    # Mock Redis client
    mock_redis_client = AsyncMock()
    mock_redis_client.ping = AsyncMock()
    mock_redis.return_value = mock_redis_client

    # Mock LLM
    mock_llm.return_value = MagicMock()

    response = client.get("/api/v1/ready")
    assert response.status_code == 503
    data = response.json()
    assert "unhealthy" in data["detail"]["services"]["postgres"]
    assert data["detail"]["ready"] is False


@patch("src.api.v1.health.get_postgres_connection")
@patch("src.api.v1.health.get_redis_client")
@patch("src.api.v1.health.LLMFactory.get_default_llm")
def test_readiness_endpoint_redis_unhealthy(mock_llm, mock_redis, mock_postgres, client):
    """Test readiness check when Redis is unhealthy."""
    # Mock PostgreSQL connection
    mock_conn = AsyncMock()
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__aenter__.return_value = mock_conn
    mock_postgres.return_value = mock_engine

    # Mock Redis client failure
    mock_redis.side_effect = Exception("Redis connection failed")

    # Mock LLM
    mock_llm.return_value = MagicMock()

    response = client.get("/api/v1/ready")
    assert response.status_code == 503
    data = response.json()
    assert "unhealthy" in data["detail"]["services"]["redis"]
    assert data["detail"]["ready"] is False


@patch("src.api.v1.health.get_postgres_connection")
@patch("src.api.v1.health.get_redis_client")
@patch("src.api.v1.health.LLMFactory.get_default_llm")
def test_readiness_endpoint_llm_unhealthy(mock_llm, mock_redis, mock_postgres, client):
    """Test readiness check when LLM is unhealthy."""
    # Mock PostgreSQL connection
    mock_conn = AsyncMock()
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__aenter__.return_value = mock_conn
    mock_postgres.return_value = mock_engine

    # Mock Redis client
    mock_redis_client = AsyncMock()
    mock_redis_client.ping = AsyncMock()
    mock_redis.return_value = mock_redis_client

    # Mock LLM failure
    mock_llm.side_effect = ValueError("OPENAI_API_KEY not found")

    response = client.get("/api/v1/ready")
    assert response.status_code == 503
    data = response.json()
    assert "unhealthy" in data["detail"]["services"]["llm"]
    assert data["detail"]["ready"] is False


@patch("src.api.v1.health.get_postgres_connection")
@patch("src.api.v1.health.get_redis_client")
@patch("src.api.v1.health.LLMFactory.get_default_llm")
def test_readiness_endpoint_multiple_services_unhealthy(mock_llm, mock_redis, mock_postgres, client):
    """Test readiness check when multiple services are unhealthy."""
    # Mock PostgreSQL connection failure
    mock_postgres.side_effect = Exception("DB connection failed")

    # Mock Redis client failure
    mock_redis.side_effect = Exception("Redis connection failed")

    # Mock LLM
    mock_llm.return_value = MagicMock()

    response = client.get("/api/v1/ready")
    assert response.status_code == 503
    data = response.json()
    assert "unhealthy" in data["detail"]["services"]["postgres"]
    assert "unhealthy" in data["detail"]["services"]["redis"]
    assert data["detail"]["services"]["llm"] == "healthy"
    assert data["detail"]["ready"] is False


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "GuardianEye API"
    assert data["status"] == "operational"
