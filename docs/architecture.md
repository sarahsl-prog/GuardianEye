# GuardianEye Architecture

## Overview

GuardianEye is an AI-powered Security Operations Center (SOC) dashboard built with Python, LangGraph, and FastAPI.

## Architecture Components

### 1. Multi-Agent System

The system uses a hierarchical multi-agent architecture:

- **Level 1: Main Supervisor** - Routes requests to appropriate teams
- **Level 2: Team Supervisors** - Coordinate specialist agents within teams
  - Security Operations Team
  - Threat Intelligence Team
  - Governance Team
- **Level 3: Specialist Agents** - Execute specific security tasks

### 2. Core Technologies

- **LangGraph**: Multi-agent orchestration with state management
- **LangChain**: LLM abstractions and integrations
- **FastAPI**: REST API framework
- **PostgreSQL**: State persistence and checkpointing
- **Redis**: Caching and async task queue
- **Chroma**: Vector database for knowledge base

### 3. LLM Provider Support

The system supports multiple LLM providers:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3.5)
- Google (Gemini 2.0)
- Ollama (Local models)
- LMStudio (Local models)

## Directory Structure

See the main README.md for the complete directory structure.

## Key Design Principles

1. **Modularity**: Each component is self-contained and testable
2. **Flexibility**: Switch LLM providers without code changes
3. **Scalability**: Hierarchical design supports unlimited agents
4. **Observability**: Built-in logging and monitoring
5. **Type Safety**: Pydantic models for all data validation

## State Management

LangGraph manages conversation state with:
- Message history
- User context
- Routing information
- Intermediate results
- Execution metadata

State is persisted using checkpointers (SQLite for dev, PostgreSQL for production).

## API Design

RESTful API with the following endpoints:
- `/health` - Health check
- `/api/v1/agents/execute` - Execute agent with auto-routing
- `/api/v1/agents/{agent_name}` - Execute specific agent
- `/api/v1/agents/list` - List all available agents

See the [API Documentation](./api.md) for more details.
