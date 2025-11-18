# GuardianEye: Python + LangGraph Architecture Redesign Report

**Date:** November 18, 2025
**Prepared By:** Claude (Architecture Analysis)
**Project:** GuardianEye - AI-Powered Security Operations Center Dashboard

---

## Executive Summary

This report outlines a comprehensive redesign of the GuardianEye application from a Next.js/TypeScript/Google Genkit stack to a Python-based architecture using LangGraph for multi-agent orchestration. The new architecture provides superior flexibility, extensibility, and supports both local and cloud LLM deployments while maintaining all existing functionality.

**Key Benefits:**
- **Unified Python Ecosystem**: Single language for AI/ML workflows
- **Advanced Agent Orchestration**: LangGraph's stateful, graph-based workflows
- **LLM Flexibility**: Seamless switching between local (Ollama, LMStudio) and cloud (OpenAI, Anthropic, Google) LLMs
- **Production-Ready**: Built-in state persistence, checkpointing, and monitoring
- **Extensibility**: Clean architecture enabling rapid addition of new agents
- **Cost Efficiency**: Option to use local LLMs for sensitive data or cost reduction

---

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [New Architecture Overview](#new-architecture-overview)
3. [Technology Stack](#technology-stack)
4. [Multi-Agent Design Pattern](#multi-agent-design-pattern)
5. [Detailed File Structure](#detailed-file-structure)
6. [LLM Provider Architecture](#llm-provider-architecture)
7. [Agent Implementation Guide](#agent-implementation-guide)
8. [State Management & Persistence](#state-management--persistence)
9. [API Design](#api-design)
10. [Security Considerations](#security-considerations)
11. [Deployment Architecture](#deployment-architecture)
12. [Migration Strategy](#migration-strategy)
13. [Development Roadmap](#development-roadmap)
14. [References & Research](#references--research)

---

## 1. Current State Analysis

### Existing Architecture
- **Frontend**: Next.js 15.3.3 with React 18 and TypeScript
- **AI Framework**: Google Genkit 1.20.0
- **LLM**: Google Gemini 2.5 Flash (cloud-only)
- **Backend**: Firebase (database and auth)
- **Deployment**: Firebase App Hosting

### Current Agents
1. **Incident Triage** - Summarizes alerts and suggests actions
2. **Threat Hunting** - Generates threat hunting hypotheses
3. **Anomaly Investigation** - Analyzes logs against baselines
4. **Security Knowledge** - NLP Q&A about security architecture
5. **Compliance Auditor** - Summarizes compliance findings

### Limitations of Current Architecture
1. **Vendor Lock-in**: Tightly coupled to Google's Genkit and Gemini
2. **No Local LLM Support**: Cannot run offline or with private models
3. **Limited Agent Coordination**: Agents operate independently without inter-agent communication
4. **JavaScript/TypeScript**: Less mature AI/ML ecosystem compared to Python
5. **State Management**: Limited workflow state persistence and recovery
6. **Scalability**: Firebase constraints for high-volume SOC operations

---

## 2. New Architecture Overview

### Design Philosophy
The new architecture embraces a **hierarchical multi-agent system** with Python and LangGraph at its core, providing:

1. **Modularity**: Each agent is a self-contained, testable unit
2. **Orchestration**: Supervisor agents coordinate specialized agents
3. **State Management**: Full conversation and workflow state persistence
4. **Flexibility**: Switch LLM providers without code changes
5. **Observability**: Built-in logging, tracing, and monitoring
6. **Production-Ready**: Designed for enterprise SOC deployments

### Architecture Diagram (Conceptual)

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React/Next.js)                 │
│                    (Can remain or be rebuilt)                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │ REST/WebSocket API
┌───────────────────────────▼─────────────────────────────────────┐
│                      FastAPI Backend                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              API Routes & Authentication                    │ │
│  └────────────────────┬───────────────────────────────────────┘ │
└───────────────────────┼─────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                   LangGraph Orchestration Layer                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Supervisor Agent (Main Coordinator)             │  │
│  └───┬──────────────────────────────────────────────────┬───┘  │
│      │                                                    │      │
│  ┌───▼────────────┐  ┌─────────────┐  ┌────────────────▼───┐  │
│  │ Security Team  │  │ Compliance  │  │ Intelligence Team  │  │
│  │   Supervisor   │  │    Team     │  │    Supervisor      │  │
│  └───┬────────────┘  └──────┬──────┘  └────────────┬───────┘  │
│      │                      │                       │          │
│  ┌───▼─────┐ ┌──────┐  ┌───▼──────┐  ┌─────┐  ┌───▼──────┐  │
│  │Incident │ │Anomaly│ │Compliance│  │Threat│  │Security  │  │
│  │ Triage  │ │Invest.│ │ Auditor  │  │Hunt  │  │Knowledge │  │
│  └─────────┘ └──────┘  └──────────┘  └─────┘  └──────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    LLM Provider Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌─────────┐  ┌─────────────────┐ │
│  │  OpenAI  │  │Anthropic │  │ Google  │  │ Local (Ollama)  │ │
│  └──────────┘  └──────────┘  └─────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                   State Persistence Layer                        │
│  ┌──────────────┐  ┌─────────────┐  ┌────────────────────────┐ │
│  │ PostgreSQL   │  │   Redis     │  │  Vector DB (Chroma)    │ │
│  │ (Checkpoints)│  │  (Cache)    │  │  (Knowledge Base)      │ │
│  └──────────────┘  └─────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Runtime** | Python | 3.11+ | Core language |
| **Agent Framework** | LangGraph | 0.2.x | Multi-agent orchestration |
| **LLM Integration** | LangChain | 0.3.x | LLM abstractions |
| **Web Framework** | FastAPI | 0.115+ | REST API server |
| **State Storage** | PostgreSQL | 16+ | Production state persistence |
| **Cache/Queue** | Redis | 7+ | Caching and async tasks |
| **Vector DB** | Chroma | 0.5.x | Embeddings and semantic search |
| **Validation** | Pydantic | 2.x | Data validation and settings |
| **Async** | asyncio | stdlib | Async/await patterns |
| **HTTP Client** | httpx | 0.27+ | Async HTTP requests |
| **Testing** | pytest | 8.x | Unit and integration tests |
| **Containerization** | Docker | 24+ | Deployment packaging |

### LLM Provider SDKs

| Provider | SDK | Purpose |
|----------|-----|---------|
| **OpenAI** | `langchain-openai` | GPT-4, GPT-3.5 |
| **Anthropic** | `langchain-anthropic` | Claude 3.5 Sonnet, Opus |
| **Google** | `langchain-google-genai` | Gemini 2.5 Flash/Pro |
| **Local (Ollama)** | `langchain-ollama` | Llama 3.1, Mistral, etc. |
| **Local (LMStudio)** | `langchain-openai` | Any LMStudio model |

### Development Tools

- **Dependency Management**: `uv` or `poetry`
- **Code Formatting**: `ruff` (linter + formatter)
- **Type Checking**: `mypy`
- **Environment Management**: `python-dotenv`
- **API Documentation**: FastAPI auto-generates OpenAPI/Swagger
- **Monitoring**: LangSmith (optional) for LangGraph observability

---

## 4. Multi-Agent Design Pattern

### Pattern Selection: Hierarchical Supervisor Architecture

Based on LangGraph best practices research, we adopt a **hierarchical supervisor pattern** for the following reasons:

1. **Scalability**: Easily add new agents without overwhelming a single supervisor
2. **Domain Separation**: Group related agents (e.g., all threat detection agents)
3. **Fault Isolation**: Issues in one team don't affect other teams
4. **Specialized Coordination**: Each supervisor optimized for its domain

### Three-Tier Hierarchy

```
Level 1: Main Supervisor
    ├─ Routes user requests to appropriate team
    ├─ Aggregates results from multiple teams
    └─ Handles cross-team coordination

Level 2: Team Supervisors (3-4 teams)
    ├─ Security Operations Team (Incident, Anomaly, Vulnerability)
    ├─ Threat Intelligence Team (Threat Hunting, Recon)
    ├─ Governance Team (Compliance, Knowledge)
    └─ [Future teams can be added here]

Level 3: Specialist Agents (5+ agents)
    ├─ Incident Triage Agent
    ├─ Anomaly Investigation Agent
    ├─ Threat Hunting Agent
    ├─ Compliance Auditor Agent
    ├─ Security Knowledge Agent
    └─ [Future agents can be added here]
```

### Agent Communication Flow

1. **User Request** → Main Supervisor
2. **Main Supervisor** analyzes request and routes to appropriate Team Supervisor
3. **Team Supervisor** delegates to one or more Specialist Agents
4. **Specialist Agents** execute tasks and return results to Team Supervisor
5. **Team Supervisor** aggregates and returns to Main Supervisor
6. **Main Supervisor** formats final response to user

### State Sharing

All agents share a **common state object** that includes:
- **User Context**: Current user, session ID, permissions
- **Conversation History**: Full message thread
- **Intermediate Results**: Outputs from previous agents
- **Tool Call History**: Audit trail of actions taken
- **Metadata**: Timestamps, execution time, costs

---

## 5. Detailed File Structure

```
guardianEye-python/
│
├── .env                              # Environment variables (API keys, DB URLs)
├── .env.example                      # Example environment file
├── .gitignore                        # Git ignore patterns
├── pyproject.toml                    # Python project config (uv/poetry)
├── requirements.txt                  # Pip dependencies (auto-generated)
├── README.md                         # Project documentation
├── docker-compose.yml                # Local dev environment
├── Dockerfile                        # Production container
│
├── src/
│   ├── __init__.py
│   │
│   ├── main.py                       # FastAPI application entry point
│   │
│   ├── config/                       # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py               # Pydantic settings (from .env)
│   │   ├── llm_providers.py          # LLM provider configurations
│   │   └── agent_registry.py         # Central agent registration
│   │
│   ├── core/                         # Core functionality
│   │   ├── __init__.py
│   │   ├── llm_factory.py            # LLM provider factory pattern
│   │   ├── state.py                  # Shared state definitions
│   │   ├── prompts.py                # Centralized prompt templates
│   │   ├── checkpointer.py           # State persistence setup
│   │   └── exceptions.py             # Custom exceptions
│   │
│   ├── agents/                       # All agent implementations
│   │   ├── __init__.py
│   │   │
│   │   ├── base/                     # Base agent classes
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py         # Abstract agent interface
│   │   │   ├── base_supervisor.py    # Abstract supervisor interface
│   │   │   └── tools.py              # Shared tool definitions
│   │   │
│   │   ├── supervisors/              # Supervisor agents
│   │   │   ├── __init__.py
│   │   │   ├── main_supervisor.py    # Level 1: Main coordinator
│   │   │   ├── security_ops_supervisor.py    # Level 2: Security team
│   │   │   ├── threat_intel_supervisor.py    # Level 2: Threat team
│   │   │   └── governance_supervisor.py      # Level 2: Compliance team
│   │   │
│   │   ├── specialists/              # Specialist agents (Level 3)
│   │   │   ├── __init__.py
│   │   │   ├── incident_triage.py    # Incident analysis agent
│   │   │   ├── anomaly_investigation.py  # Anomaly detection agent
│   │   │   ├── threat_hunting.py     # Threat hunting agent
│   │   │   ├── compliance_auditor.py # Compliance checking agent
│   │   │   ├── security_knowledge.py # Knowledge Q&A agent
│   │   │   ├── vulnerability_prioritization.py
│   │   │   └── recon_orchestrator.py
│   │   │
│   │   └── graphs/                   # LangGraph graph definitions
│   │       ├── __init__.py
│   │       ├── main_graph.py         # Main supervisor graph
│   │       ├── security_ops_graph.py # Security team graph
│   │       ├── threat_intel_graph.py # Threat team graph
│   │       └── governance_graph.py   # Governance team graph
│   │
│   ├── api/                          # FastAPI routes
│   │   ├── __init__.py
│   │   ├── deps.py                   # Dependency injection
│   │   ├── middleware.py             # Custom middleware
│   │   │
│   │   ├── v1/                       # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── router.py             # Main router
│   │   │   ├── agents.py             # Agent execution endpoints
│   │   │   ├── health.py             # Health check endpoints
│   │   │   ├── auth.py               # Authentication endpoints
│   │   │   └── websocket.py          # WebSocket for streaming
│   │   │
│   │   └── schemas/                  # Pydantic schemas (request/response)
│   │       ├── __init__.py
│   │       ├── agent_request.py
│   │       ├── agent_response.py
│   │       └── common.py
│   │
│   ├── services/                     # Business logic services
│   │   ├── __init__.py
│   │   ├── agent_service.py          # Agent execution service
│   │   ├── auth_service.py           # Authentication service
│   │   └── knowledge_service.py      # Knowledge base service
│   │
│   ├── db/                           # Database and persistence
│   │   ├── __init__.py
│   │   ├── postgres.py               # PostgreSQL connection
│   │   ├── redis.py                  # Redis connection
│   │   ├── vector_store.py           # Chroma vector DB
│   │   └── models.py                 # SQLAlchemy models (if needed)
│   │
│   └── utils/                        # Utility functions
│       ├── __init__.py
│       ├── logging.py                # Logging configuration
│       ├── metrics.py                # Metrics collection
│       └── validators.py             # Custom validators
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── conftest.py                   # Pytest fixtures
│   ├── unit/                         # Unit tests
│   │   ├── test_agents/
│   │   ├── test_core/
│   │   └── test_services/
│   ├── integration/                  # Integration tests
│   │   ├── test_api/
│   │   └── test_graphs/
│   └── e2e/                          # End-to-end tests
│       └── test_workflows.py
│
├── scripts/                          # Utility scripts
│   ├── setup_db.py                   # Database initialization
│   ├── seed_data.py                  # Seed test data
│   └── run_dev.sh                    # Development startup script
│
├── docs/                             # Documentation
│   ├── architecture.md               # Architecture overview
│   ├── agent_guide.md                # Guide to adding new agents
│   ├── deployment.md                 # Deployment instructions
│   └── api.md                        # API documentation
│
└── frontend/                         # Frontend (optional - can keep existing)
    ├── [Existing Next.js app or new React app]
    └── [Points to Python backend API]
```

### Key Design Principles

1. **Separation of Concerns**: Clear boundaries between API, agents, services, and data
2. **Dependency Injection**: FastAPI's DI system for testability
3. **Type Safety**: Pydantic models everywhere for validation
4. **Testability**: All components have dedicated test directories
5. **Scalability**: Services can be split into microservices later
6. **Extensibility**: New agents added without modifying existing code

---

## 6. LLM Provider Architecture

### Provider Factory Pattern

The application uses a **factory pattern** to abstract LLM provider selection:

```python
# src/core/llm_factory.py

from enum import Enum
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"

class LLMFactory:
    @staticmethod
    def create_llm(
        provider: LLMProvider,
        model: str | None = None,
        temperature: float = 0.7,
        **kwargs
    ) -> BaseChatModel:
        """Create LLM instance based on provider."""

        if provider == LLMProvider.OPENAI:
            return ChatOpenAI(
                model=model or "gpt-4-turbo-preview",
                temperature=temperature,
                **kwargs
            )

        elif provider == LLMProvider.ANTHROPIC:
            return ChatAnthropic(
                model=model or "claude-3-5-sonnet-20241022",
                temperature=temperature,
                **kwargs
            )

        elif provider == LLMProvider.GOOGLE:
            return ChatGoogleGenerativeAI(
                model=model or "gemini-2.5-flash",
                temperature=temperature,
                **kwargs
            )

        elif provider == LLMProvider.OLLAMA:
            return ChatOllama(
                model=model or "llama3.1:8b",
                temperature=temperature,
                base_url=kwargs.get("base_url", "http://localhost:11434"),
                **kwargs
            )

        elif provider == LLMProvider.LMSTUDIO:
            # LMStudio uses OpenAI-compatible API
            return ChatOpenAI(
                model=model or "local-model",
                temperature=temperature,
                base_url=kwargs.get("base_url", "http://localhost:1234/v1"),
                api_key="lm-studio",  # LMStudio doesn't validate
                **kwargs
            )

        else:
            raise ValueError(f"Unknown provider: {provider}")
```

### Environment Configuration

```bash
# .env file structure

# ===== LLM Provider Selection =====
LLM_PROVIDER=ollama                    # Options: openai, anthropic, google, ollama, lmstudio
LLM_MODEL=llama3.1:8b                  # Model name (provider-specific)
LLM_TEMPERATURE=0.7

# ===== Cloud Provider API Keys =====
OPENAI_API_KEY=sk-...                  # Only needed if LLM_PROVIDER=openai
ANTHROPIC_API_KEY=sk-ant-...           # Only needed if LLM_PROVIDER=anthropic
GOOGLE_API_KEY=AIza...                 # Only needed if LLM_PROVIDER=google

# ===== Local LLM Configuration =====
OLLAMA_BASE_URL=http://localhost:11434       # Ollama server URL
LMSTUDIO_BASE_URL=http://localhost:1234/v1   # LMStudio server URL

# ===== Database Configuration =====
POSTGRES_URL=postgresql://user:pass@localhost:5432/guardianEye
REDIS_URL=redis://localhost:6379/0
CHROMA_PERSIST_DIRECTORY=./data/chroma

# ===== Application Configuration =====
APP_ENV=development                    # development, staging, production
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# ===== Security =====
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Multi-Provider Support Strategy

**Development/Testing**: Use local Ollama with Llama 3.1
**Production (Cost-Sensitive)**: Use local Ollama or Google Gemini Flash
**Production (Performance)**: Use Anthropic Claude 3.5 Sonnet or OpenAI GPT-4
**Air-Gapped/Secure**: Use local LMStudio with private models

**Agent-Specific Overrides**: Some agents can use different models:
```python
# Example: Use GPT-4 for complex reasoning, Llama for simple tasks
incident_triage_llm = LLMFactory.create_llm(LLMProvider.OPENAI, "gpt-4")
knowledge_base_llm = LLMFactory.create_llm(LLMProvider.OLLAMA, "llama3.1:8b")
```

---

## 7. Agent Implementation Guide

### Base Agent Interface

```python
# src/agents/base/base_agent.py

from abc import ABC, abstractmethod
from typing import Any, Dict
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel

class AgentInput(BaseModel):
    """Base input schema for all agents."""
    query: str
    context: Dict[str, Any] = {}

class AgentOutput(BaseModel):
    """Base output schema for all agents."""
    result: str
    metadata: Dict[str, Any] = {}
    next_agent: str | None = None

class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, llm: BaseChatModel, name: str):
        self.llm = llm
        self.name = name

    @abstractmethod
    async def process(self, input: AgentInput) -> AgentOutput:
        """Process input and return output."""
        pass

    @abstractmethod
    def get_prompt_template(self) -> str:
        """Return the prompt template for this agent."""
        pass
```

### Example Specialist Agent

```python
# src/agents/specialists/incident_triage.py

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.agents.base.base_agent import BaseAgent, AgentInput, AgentOutput
from pydantic import BaseModel, Field

class IncidentTriageInput(AgentInput):
    """Input for incident triage agent."""
    alert_details: str = Field(..., description="Raw alert details")
    alert_severity: str = Field(default="medium", description="Alert severity level")

class IncidentTriageOutput(AgentOutput):
    """Output from incident triage agent."""
    summary: str
    suggested_actions: list[str]
    priority: str

class IncidentTriageAgent(BaseAgent):
    """Agent for analyzing security incidents and suggesting responses."""

    def __init__(self, llm):
        super().__init__(llm, name="incident_triage")

    def get_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """You are a senior security analyst specializing in incident triage.
            Analyze the security alert and provide:
            1. A clear summary of the incident
            2. Specific recommended actions
            3. Priority level (critical, high, medium, low)

            Be concise and actionable."""),
            ("user", """Alert Details: {alert_details}
            Severity: {alert_severity}

            Please analyze this incident.""")
        ])

    async def process(self, input: IncidentTriageInput) -> IncidentTriageOutput:
        """Process incident triage request."""

        # Create chain
        chain = self.get_prompt_template() | self.llm | StrOutputParser()

        # Execute
        response = await chain.ainvoke({
            "alert_details": input.alert_details,
            "alert_severity": input.alert_severity
        })

        # Parse response (simplified - would use structured output in production)
        # For production, use llm.with_structured_output(IncidentTriageOutput)

        return IncidentTriageOutput(
            result=response,
            summary="[Extracted from response]",
            suggested_actions=["[Extracted from response]"],
            priority="high",
            metadata={"agent": self.name, "model": self.llm.model_name}
        )
```

### Adding a New Agent (Step-by-Step)

1. **Create agent file**: `src/agents/specialists/new_agent.py`
2. **Inherit from BaseAgent**: Define input/output schemas
3. **Implement `process()` method**: Core logic
4. **Define prompt template**: In `get_prompt_template()`
5. **Register in agent registry**: Add to `src/config/agent_registry.py`
6. **Update supervisor**: Add routing logic in appropriate team supervisor
7. **Add API endpoint**: Create endpoint in `src/api/v1/agents.py`
8. **Write tests**: Add unit tests in `tests/unit/test_agents/`
9. **Document**: Update `docs/agent_guide.md`

**Time to add new agent**: ~30-60 minutes

---

## 8. State Management & Persistence

### LangGraph State Schema

```python
# src/core/state.py

from typing import Annotated, TypedDict, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

class GuardianEyeState(TypedDict):
    """Shared state across all agents."""

    # Conversation
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # User context
    user_id: str
    session_id: str

    # Routing
    current_team: str | None
    current_agent: str | None

    # Results
    intermediate_results: dict[str, any]
    final_result: str | None

    # Metadata
    execution_path: list[str]
    tool_calls: list[dict]
    total_tokens: int
    start_time: float
```

### Checkpointing Setup

```python
# src/core/checkpointer.py

from langgraph.checkpoint.postgres import AsyncPostgresSaver
from langgraph.checkpoint.sqlite import AsyncSqliteSaver
from src.config.settings import settings

async def get_checkpointer():
    """Get appropriate checkpointer based on environment."""

    if settings.APP_ENV == "production":
        # PostgreSQL for production
        checkpointer = AsyncPostgresSaver.from_conn_string(
            settings.POSTGRES_URL
        )
        await checkpointer.setup()
        return checkpointer

    else:
        # SQLite for development
        checkpointer = AsyncSqliteSaver.from_conn_string(
            "checkpoints.db"
        )
        await checkpointer.setup()
        return checkpointer
```

### State Persistence Benefits

1. **Conversation History**: Full context across requests
2. **Error Recovery**: Resume from last checkpoint on failure
3. **Human-in-the-Loop**: Pause for approval, resume after
4. **Time Travel**: Replay or debug past executions
5. **Audit Trail**: Complete record of all agent actions

---

## 9. API Design

### FastAPI Application Structure

```python
# src/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.router import api_router
from src.api.middleware import logging_middleware
from src.config.settings import settings

app = FastAPI(
    title="GuardianEye API",
    description="AI-Powered Security Operations Center",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.middleware("http")(logging_middleware)

# Routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}
```

### Key API Endpoints

```python
# src/api/v1/agents.py

from fastapi import APIRouter, Depends
from src.api.schemas.agent_request import AgentRequest
from src.api.schemas.agent_response import AgentResponse
from src.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/incident-triage", response_model=AgentResponse)
async def run_incident_triage(
    request: AgentRequest,
    service: AgentService = Depends()
):
    """Execute incident triage agent."""
    result = await service.execute_agent("incident_triage", request)
    return result

@router.post("/threat-hunting", response_model=AgentResponse)
async def run_threat_hunting(
    request: AgentRequest,
    service: AgentService = Depends()
):
    """Execute threat hunting agent."""
    result = await service.execute_agent("threat_hunting", request)
    return result

@router.post("/execute", response_model=AgentResponse)
async def execute_agent(
    agent_name: str,
    request: AgentRequest,
    service: AgentService = Depends()
):
    """Generic agent execution endpoint."""
    result = await service.execute_agent(agent_name, request)
    return result

# WebSocket for streaming responses
from fastapi import WebSocket

@router.websocket("/stream/{agent_name}")
async def stream_agent(
    websocket: WebSocket,
    agent_name: str,
    service: AgentService = Depends()
):
    """Stream agent responses in real-time."""
    await websocket.accept()
    async for chunk in service.stream_agent(agent_name, websocket):
        await websocket.send_json(chunk)
```

### Request/Response Schemas

```python
# src/api/schemas/agent_request.py

from pydantic import BaseModel, Field

class AgentRequest(BaseModel):
    """Standard agent request."""
    query: str = Field(..., description="User query or input")
    context: dict = Field(default_factory=dict, description="Additional context")
    session_id: str | None = Field(None, description="Session ID for state persistence")
    stream: bool = Field(False, description="Enable streaming responses")

# src/api/schemas/agent_response.py

class AgentResponse(BaseModel):
    """Standard agent response."""
    result: str
    agent_name: str
    execution_time: float
    tokens_used: int | None = None
    metadata: dict = {}
```

---

## 10. Security Considerations

### Authentication & Authorization

```python
# src/api/deps.py (Dependency Injection)

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.services.auth_service import verify_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verify JWT token and return current user."""
    token = credentials.credentials
    user = await verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user

# Usage in endpoints:
@router.post("/agents/execute")
async def execute_agent(
    request: AgentRequest,
    current_user = Depends(get_current_user)  # Requires auth
):
    # Only authenticated users can execute agents
    ...
```

### API Key Security

1. **Environment Variables**: All keys in `.env`, never committed
2. **Secret Management**: Use AWS Secrets Manager or HashiCorp Vault in production
3. **Rotation**: Implement API key rotation policies
4. **Least Privilege**: Each LLM provider key has minimal permissions

### Input Validation

- **Pydantic**: All inputs validated with strict schemas
- **SQL Injection**: Use SQLAlchemy ORM (never raw SQL)
- **Prompt Injection**: Sanitize user inputs before sending to LLMs
- **Rate Limiting**: Implement per-user rate limits with Redis

### Audit Logging

```python
# Log all agent executions
logger.info({
    "event": "agent_execution",
    "user_id": user.id,
    "agent": agent_name,
    "timestamp": datetime.utcnow(),
    "input_hash": hash(request.query),
    "execution_time": duration
})
```

---

## 11. Deployment Architecture

### Development Environment

```yaml
# docker-compose.yml

services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - postgres
      - redis
      - ollama
    volumes:
      - ./src:/app/src  # Hot reload

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: guardianEye
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  postgres_data:
  ollama_data:
```

**Start development**: `docker-compose up`

### Production Deployment Options

#### Option 1: Cloud Platform (AWS, GCP, Azure)

```
┌─────────────────────────────────────────────────┐
│              Load Balancer (ALB/NGINX)          │
└───────────────────┬─────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
    ┌───▼───┐   ┌───▼───┐   ┌───▼───┐
    │FastAPI│   │FastAPI│   │FastAPI│  (Auto-scaling)
    │  Pod  │   │  Pod  │   │  Pod  │
    └───┬───┘   └───┬───┘   └───┬───┘
        │           │           │
        └───────────┼───────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
    ┌───▼───────┐ ┌─▼─────┐ ┌──▼──────┐
    │ PostgreSQL│ │ Redis │ │ Ollama  │
    │   (RDS)   │ │(Elast.)│ │ (EKS)  │
    └───────────┘ └───────┘ └─────────┘
```

**Deployment**: Kubernetes (EKS, GKE, AKS) with Helm charts

#### Option 2: Serverless (AWS Lambda + API Gateway)

- Use **AWS Lambda** with FastAPI (using Mangum adapter)
- **API Gateway** for HTTP endpoints
- **RDS Proxy** for PostgreSQL connection pooling
- **ElastiCache** for Redis
- **ECS Fargate** for Ollama (if using local LLMs)

#### Option 3: Traditional VPS (DigitalOcean, Linode)

- Single server or small cluster
- Docker Compose for orchestration
- NGINX reverse proxy
- Certbot for SSL

### Monitoring & Observability

1. **Application Metrics**: Prometheus + Grafana
2. **LLM Observability**: LangSmith (official LangGraph monitoring)
3. **Error Tracking**: Sentry
4. **Logging**: ELK stack (Elasticsearch, Logstash, Kibana)
5. **Uptime**: UptimeRobot or Datadog

---

## 12. Migration Strategy

### Phase 1: Parallel Development (2-3 weeks)

1. **Week 1**: Build Python backend infrastructure
   - Set up FastAPI skeleton
   - Configure LLM providers
   - Implement 1-2 agents as proof of concept

2. **Week 2**: Port all agents
   - Migrate all 5 existing agents to Python/LangGraph
   - Implement supervisor hierarchy
   - Add state persistence

3. **Week 3**: API parity
   - Ensure all existing endpoints work
   - Add authentication
   - Write tests

### Phase 2: Integration (1 week)

1. **Frontend Adaptation**:
   - Update API URLs to point to Python backend
   - Test all features end-to-end
   - Fix any breaking changes

2. **Data Migration** (if needed):
   - Export data from Firebase
   - Import to PostgreSQL

### Phase 3: Deployment (1 week)

1. **Staging Deployment**:
   - Deploy to staging environment
   - Run load tests
   - Gather feedback

2. **Production Cutover**:
   - Blue-green deployment
   - Gradual traffic shift (10% → 50% → 100%)
   - Monitor metrics

### Phase 4: Optimization (Ongoing)

1. **Performance Tuning**:
   - Optimize slow agents
   - Add caching where appropriate
   - Fine-tune prompts

2. **Feature Additions**:
   - Add new agents
   - Implement advanced features (multi-agent collaboration)

### Rollback Plan

- Keep Next.js backend running in parallel for 1 month
- If critical issues, instant rollback via load balancer
- PostgreSQL can export to Firebase format if needed

---

## 13. Development Roadmap

### Immediate (Month 1)

- [ ] Set up Python project structure
- [ ] Implement LLM factory with all providers
- [ ] Create base agent and supervisor classes
- [ ] Port incident triage agent
- [ ] Set up PostgreSQL checkpointing
- [ ] Build FastAPI skeleton with 1-2 endpoints

### Short-term (Months 2-3)

- [ ] Port all remaining agents
- [ ] Implement full supervisor hierarchy
- [ ] Add authentication and authorization
- [ ] Build comprehensive test suite
- [ ] Set up Docker development environment
- [ ] Create API documentation

### Medium-term (Months 4-6)

- [ ] Deploy to staging environment
- [ ] Implement monitoring and observability
- [ ] Add WebSocket streaming support
- [ ] Build admin dashboard for agent management
- [ ] Optimize prompts and agent performance
- [ ] Load testing and performance tuning

### Long-term (Months 7-12)

- [ ] Multi-agent collaboration (agents calling each other)
- [ ] Advanced RAG with vector database
- [ ] Custom tool development for agents
- [ ] Fine-tune local models for specific tasks
- [ ] Implement feedback loop and continuous learning
- [ ] Scale to handle 1000+ concurrent users

---

## 14. References & Research

### Key Resources

1. **LangGraph Documentation**
   - Official docs: https://langchain-ai.github.io/langgraph/
   - Multi-agent patterns: https://docs.langchain.com/oss/python/langchain/multi-agent

2. **Best Practices**
   - "Advanced Multi-Agent Development with LangGraph: Expert Guide & Best Practices 2025"
   - "Building Production-Ready AI APIs with FastAPI and LangGraph"
   - "Benchmarking Multi-Agent Architectures" (LangChain blog)

3. **Implementation Examples**
   - GitHub: `wassim249/fastapi-langgraph-agent-production-ready-template`
   - GitHub: `langchain-ai/local-deep-researcher`
   - "Llama 3.1 Agent using LangGraph and Ollama" (Pinecone)

4. **State Management**
   - LangGraph Checkpointing Architecture (DeepWiki)
   - "Using PostgreSQL with LangGraph for State Management and Vector Storage"

5. **Deployment**
   - "FastAPI Production Deployment - 2025 Complete Guide"
   - "Deploy A LangGraph AI Agent In 5 Minutes (For Free!)"

### Technologies Evaluated

| Technology | Chosen? | Reason |
|------------|---------|--------|
| LangGraph | ✅ Yes | Best-in-class multi-agent orchestration |
| FastAPI | ✅ Yes | Modern, fast, auto-documented APIs |
| PostgreSQL | ✅ Yes | Production-grade state persistence |
| Ollama | ✅ Yes | Local LLM support |
| Redis | ✅ Yes | Caching and async task queue |
| Chroma | ✅ Yes | Lightweight vector DB for knowledge base |
| ~~CrewAI~~ | ❌ No | Less flexible than LangGraph |
| ~~AutoGen~~ | ❌ No | Less production-ready |
| ~~Flask~~ | ❌ No | FastAPI is more modern |

---

## Conclusion

This redesigned architecture transforms GuardianEye into a **production-ready, enterprise-grade security platform** with:

✅ **Python-native**: Leverage the full AI/ML ecosystem
✅ **LangGraph-powered**: Advanced multi-agent orchestration with state management
✅ **LLM-agnostic**: Switch between local (Ollama) and cloud (OpenAI, Anthropic, Google) LLMs
✅ **Scalable**: Hierarchical agent architecture supports unlimited growth
✅ **Extensible**: Add new agents in ~30-60 minutes
✅ **Secure**: Environment-based config, authentication, input validation
✅ **Observable**: Built-in logging, tracing, and monitoring
✅ **Production-ready**: State persistence, error recovery, human-in-the-loop

### Estimated Development Time

- **Minimal Viable Product (MVP)**: 3-4 weeks (1 developer)
- **Feature Parity with Current App**: 6-8 weeks (1 developer)
- **Production-Ready with All Features**: 10-12 weeks (1-2 developers)

### Estimated Costs

**Development Environment**: Free (local Ollama)
**Production (Cloud LLM)**: $50-500/month depending on usage
**Production (Local LLM)**: $100-200/month (server costs only)

### Next Steps

1. **Approval**: Review this architecture with stakeholders
2. **Environment Setup**: Set up development environment (Docker, PostgreSQL, Ollama)
3. **POC**: Build proof-of-concept with 1-2 agents
4. **Iteration**: Gather feedback and refine architecture
5. **Full Build**: Implement all agents and features
6. **Deploy**: Roll out to production

---

**Document Version**: 1.0
**Last Updated**: November 18, 2025
**Author**: Claude (Architecture Analysis)
**Status**: Draft for Review
