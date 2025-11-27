# 🛡️ GuardianEye - AI-Powered Security Operations Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://github.com/langchain-ai/langgraph)

**GuardianEye** is a next-generation Security Operations Center (SOC) platform powered by multi-agent AI orchestration. Built with Python, LangGraph, and FastAPI, it provides intelligent security analysis, automated incident response, and proactive threat hunting through a hierarchical team of specialized AI agents.

## ✨ Key Features

### 🤖 Multi-Agent Architecture
- **3-Tier Hierarchical Supervision**: Main Supervisor → Team Supervisors → Specialist Agents
- **7 Specialized Security Agents**: Each expert in a specific security domain
- **Intelligent Routing**: Automatic request routing based on content analysis
- **State Persistence**: Full conversation history and workflow recovery

### 🔍 Security Capabilities
- **Incident Triage**: Automated alert analysis and response recommendations
- **Threat Hunting**: Proactive threat detection and hypothesis generation
- **Anomaly Investigation**: Behavioral analysis and deviation detection
- **Compliance Auditing**: Framework-based compliance assessment
- **Vulnerability Prioritization**: Risk-based vulnerability management
- **Security Knowledge**: RAG-powered security Q&A
- **Reconnaissance Orchestration**: Coordinated information gathering

### 🚀 Technical Highlights
- **Multi-LLM Support**: OpenAI, Anthropic, Google, Ollama, LMStudio
- **Local & Cloud**: Run completely offline or in the cloud
- **RAG with Vector Store**: Chroma-powered semantic search
- **Production-Ready**: PostgreSQL state persistence, Redis caching
- **JWT Authentication**: Secure API access
- **Docker & Kubernetes**: Full containerization support

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Backend                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Main Supervisor (Level 1)                      │ │
│  └───┬──────────────────────────────────────────────────┬─────┘ │
│      │                                                    │       │
│  ┌───▼─────────────┐  ┌─────────────┐  ┌───────────────▼────┐  │
│  │ Security Ops    │  │ Governance  │  │ Threat Intel       │  │
│  │ Team Supervisor │  │ Team Super. │  │ Team Supervisor    │  │
│  └───┬─────────────┘  └──────┬──────┘  └────────────┬───────┘  │
│      │                       │                       │          │
│  ┌───▼───────┐  ┌───────┐  ┌▼──────┐  ┌──────┐  ┌──▼──────┐  │
│  │ Incident  │  │Anomaly│  │Compli-│  │Threat│  │Security │  │
│  │  Triage   │  │Invest │  │ance   │  │Hunt  │  │Knowledge│  │
│  │  + Vuln   │  │       │  │       │  │+Recon│  │  (RAG)  │  │
│  └───────────┘  └───────┘  └───────┘  └──────┘  └─────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│  LLM Layer: OpenAI | Anthropic | Google | Ollama | LMStudio    │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone <your-repo-url>
cd GuardianEye

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app
```

Access the API at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python scripts/setup_db.py

# Run the application
python src/main.py
```

The `setup_db.py` script will:
- Initialize LangGraph state tables
- Test PostgreSQL and Redis connections
- Initialize Chroma vector store
- Seed security knowledge base
- Verify all services are ready

### Option 3: Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/deployment.yaml

# Check status
kubectl get pods
kubectl get services
```

## 📋 Prerequisites

- **Python**: 3.11 or higher
- **Docker**: 24+ (for containerized deployment)
- **PostgreSQL**: 16+ (for production state persistence)
- **Redis**: 7+ (for caching)
- **Ollama**: Latest (for local LLM inference, optional)

## 🔧 Configuration

### Environment Variables

Edit `.env` to configure:

```bash
# LLM Provider (openai, anthropic, google, ollama, lmstudio)
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
LLM_TEMPERATURE=0.7

# Cloud API Keys (optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...

# Database
POSTGRES_URL=postgresql+asyncpg://user:pass@localhost:5432/guardianeye
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Switching LLM Providers

**Use Local Ollama** (free, private):
```bash
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
```

**Use OpenAI GPT-4**:
```bash
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=sk-...
```

**Use Anthropic Claude**:
```bash
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-ant-...
```

## 📚 API Usage

### Authentication

```bash
# Get JWT token
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'

# Response
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Execute Security Analysis

```bash
# Incident triage
curl -X POST http://localhost:8000/api/v1/agents/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "query": "Analyze this security alert: Multiple failed login attempts from IP 192.168.1.100",
    "context": {
      "severity": "high",
      "alert_details": "50 failed SSH attempts in 5 minutes"
    }
  }'

# Threat hunting
curl -X POST http://localhost:8000/api/v1/agents/threat-hunting \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Generate threat hunting hypotheses for potential data exfiltration"
  }'

# Security knowledge (with RAG)
curl -X POST http://localhost:8000/api/v1/agents/security-knowledge \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key principles of Zero Trust Architecture?"
  }'
```

## 🗂️ Project Structure

```
GuardianEye/
├── src/
│   ├── agents/              # Multi-agent system
│   │   ├── base/            # Base agent classes
│   │   ├── specialists/     # 7 specialist agents
│   │   ├── graphs/          # LangGraph workflows
│   │   └── supervisors/     # Supervisor agents
│   ├── api/                 # FastAPI routes
│   │   ├── v1/              # API v1 endpoints
│   │   └── schemas/         # Pydantic schemas
│   ├── core/                # Core functionality
│   │   ├── llm_factory.py   # LLM provider factory
│   │   ├── state.py         # Shared state
│   │   └── checkpointer.py  # State persistence
│   ├── db/                  # Database layer
│   │   ├── postgres.py      # PostgreSQL
│   │   ├── redis.py         # Redis
│   │   └── vector_store.py  # Chroma vector DB
│   ├── services/            # Business logic
│   └── main.py              # FastAPI app
├── k8s/                     # Kubernetes manifests
├── scripts/                 # Utility scripts
├── tests/                   # Test suite
├── docker-compose.yml       # Docker Compose config
├── Dockerfile               # Docker image
└── requirements.txt         # Python dependencies
```

## 🎯 Use Cases

### 1. Automated Incident Response
```python
# Triage security alerts automatically
POST /api/v1/agents/incident-triage
{
  "query": "Suspicious PowerShell execution detected",
  "context": {
    "alert_details": "PowerShell with encoded command",
    "severity": "critical"
  }
}
```

### 2. Proactive Threat Hunting
```python
# Generate and test threat hypotheses
POST /api/v1/agents/threat-hunting
{
  "query": "Hunt for potential ransomware activity"
}
```

### 3. Compliance Auditing
```python
# Audit against security frameworks
POST /api/v1/agents/compliance-audit
{
  "query": "Audit our environment against NIST CSF",
  "context": {
    "framework": "NIST CSF",
    "findings": "..."
  }
}
```

### 4. Security Q&A with RAG
```python
# Ask security questions with context from vector store
POST /api/v1/agents/security-knowledge
{
  "query": "Explain the MITRE ATT&CK framework"
}
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_core/test_llm_factory.py

# Run specific test
pytest tests/unit/test_agents/test_incident_triage.py -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

### Test Fixtures

The test suite includes comprehensive fixtures in `tests/conftest.py`:

- `client` - FastAPI TestClient for API testing
- `mock_llm` - Mock LLM for testing agents without API calls
- `mock_llm_with_error` - Mock LLM for error handling tests
- `sample_agent_request` - Standard request payload for testing

### Test Coverage

- **Unit Tests**: LLM factory, agent logic, utilities
- **Integration Tests**: API endpoints, health checks, WebSocket streaming
- **E2E Tests**: Complete workflows and multi-agent routing

## 📊 Monitoring

GuardianEye includes built-in observability:

- **Health Checks**:
  - `/api/v1/health` - Basic health status
  - `/api/v1/ready` - Readiness probe (checks PostgreSQL, Redis, LLM)
  - `/api/v1/live` - Liveness probe
- **Structured Logging**: JSON logs with execution traces
- **Execution Metrics**: Execution time, token usage, routing paths
- **LangSmith Integration**: Optional LangGraph observability

For production deployments, configure Kubernetes probes:
```yaml
livenessProbe:
  httpGet:
    path: /api/v1/live
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /api/v1/ready
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

## 🔒 Security

- **JWT Authentication**: Secure API access
- **Input Validation**: Pydantic schema validation
- **Audit Logging**: All agent executions logged
- **Rate Limiting**: Redis-based rate limiting (optional)
- **Secret Management**: Environment-based configuration

## 🚀 Deployment

### Staging
```bash
# Set environment
export APP_ENV=staging

# Deploy with Docker Compose
docker-compose -f docker-compose.yml up -d
```

### Production (Kubernetes)
```bash
# Update secrets
kubectl create secret generic guardianeye-secrets \
  --from-literal=postgres_url="postgresql+asyncpg://..." \
  --from-literal=jwt_secret="..." \
  --from-literal=openai_api_key="sk-..."

# Deploy
kubectl apply -f k8s/
kubectl get pods
kubectl get services
```

## 📖 Documentation

- [Architecture Redesign Report](ARCHITECTURE_REDESIGN_REPORT.md) - Comprehensive design document
- API Documentation: `http://localhost:8000/docs` (auto-generated)
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- **LangGraph**: Multi-agent orchestration framework
- **LangChain**: LLM application framework
- **FastAPI**: Modern Python web framework
- **Ollama**: Local LLM inference

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/GuardianEye/issues)
- **Documentation**: [docs/](docs/)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/GuardianEye/discussions)

---

**Built with ❤️ for the security community**

**Version**: 2.0.0 | **Status**: Production Ready
