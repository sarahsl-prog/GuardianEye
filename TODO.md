# GuardianEye - TODO List

**Last Updated:** 2024-11-28
**Version:** 2.1.0
**Status:** In Development

---

## 🎯 Overview

This document tracks all outstanding tasks needed to complete the GuardianEye Security Operations Platform. Tasks are organized by priority and functional area.

---

## 🔴 Critical Priority (P0)

These items are essential for core functionality and must be completed first.

### 1. Multi-Agent Orchestration ✅ **COMPLETED**
- [x] **Integrate team graphs into main supervisor** - [main_graph.py:34-79](src/agents/graphs/main_graph.py#L34-L79)
  - ✅ Replaced placeholder team nodes with actual subgraph calls
  - ✅ Connected Security Ops, Threat Intel, and Governance team graphs
  - ✅ Implemented proper state passing between supervisors
  - ✅ Created 13 unit tests (all passing)
  - **Files:** `src/agents/graphs/main_graph.py`, `tests/unit/test_graphs/test_main_graph.py`

- [x] **Implement full graph-based routing** - [agents.py:25-68](src/api/v1/agents.py#L25-L68)
  - ✅ Replaced direct agent execution with main graph invocation via AgentService
  - ✅ Route through main supervisor for intelligent agent selection
  - ✅ Support multi-step workflows across teams
  - ✅ Created 7 integration tests (all passing)
  - **Files:** `src/api/v1/agents.py`, `tests/integration/test_graphs/test_orchestration.py`

### 2. Database Integration
- [ ] **Add PostgreSQL to docker-compose.yml** - [docker-compose.yml](docker-compose.yml)
  - Add PostgreSQL 16+ service definition
  - Configure volume persistence
  - Add health checks
  - Set proper environment variables
  - **Current Issue:** Missing Postgres service in docker-compose
  - **Files:** `docker-compose.yml`

- [ ] **Implement database models** - [models.py:27](src/db/models.py#L27)
  - Create User model for authentication
  - Create Session model for conversation persistence
  - Create AuditLog model for security tracking
  - Add SQLAlchemy table definitions
  - **Current Issue:** models.py only has TODO placeholder
  - **Files:** `src/db/models.py`

### 3. Testing Infrastructure ✅ **COMPLETED**
- [x] **Update tests to use local databases** ⭐ **(User Requested)**
  - ✅ Configured pytest fixtures for local PostgreSQL
  - ✅ Configured pytest fixtures for local Redis
  - ✅ Configured pytest fixtures for local Chroma DB
  - ✅ Added docker-compose.test.yml for test databases
  - ✅ Updated conftest.py with database setup/teardown
  - ✅ Created tests/utils.py with helper functions
  - ✅ Updated pyproject.toml with pytest configuration
  - **Files:** `tests/conftest.py`, `docker-compose.test.yml`, `tests/utils.py`, `pyproject.toml`

---

## 🟡 High Priority (P1)

Important features that enhance core functionality.

### 4. Vector Store & RAG
- [ ] **Complete KnowledgeService implementation** - [knowledge_service.py:11-50](src/services/knowledge_service.py#L11-L50)
  - Implement `add_document()` method with proper embedding
  - Implement `search()` method with semantic search
  - Implement `get_context()` method for RAG retrieval
  - Integrate with Chroma vector store
  - **Files:** `src/services/knowledge_service.py`

- [ ] **Add Chroma DB to docker-compose.yml**
  - Add Chroma service definition (optional, can use local persist)
  - Configure volume for persistence
  - Set up proper networking
  - **Files:** `docker-compose.yml`

- [ ] **Support alternative embedding models**
  - Add support for Ollama embeddings (local)
  - Add support for sentence-transformers
  - Make embedding provider configurable
  - Update settings.py with embedding configuration
  - **Files:** `src/db/vector_store.py`, `src/config/settings.py`

### 5. API Completeness
- [ ] **Add missing specialist agent endpoints**
  - Add `/api/v1/agents/anomaly-investigation` endpoint
  - Add `/api/v1/agents/vulnerability-prioritization` endpoint
  - Add `/api/v1/agents/compliance-audit` endpoint
  - Add `/api/v1/agents/recon-orchestration` endpoint
  - **Files:** `src/api/v1/agents.py`

- [ ] **Implement proper authentication system**
  - Create user database table and CRUD operations
  - Implement user registration endpoint
  - Implement password hashing and validation
  - Add refresh token support
  - Store sessions in database
  - **Files:** `src/api/v1/auth.py`, `src/services/auth_service.py`, `src/db/models.py`

### 6. Data Seeding
- [ ] **Complete seed_data.py implementation** - [seed_data.py:6-13](scripts/seed_data.py#L6-L13)
  - Implement knowledge base seeding with security documents
  - Implement user seeding (admin, demo users)
  - Add sample incident data for testing
  - Add sample threat intelligence data
  - **Files:** `scripts/seed_data.py`

---

## 🟢 Medium Priority (P2)

Features that improve usability and robustness.

### 7. Error Handling & Resilience
- [ ] **Add retry logic for LLM calls**
  - Implement exponential backoff for API failures
  - Add circuit breaker pattern for external services
  - Handle rate limiting gracefully
  - Add fallback responses for critical failures
  - **Files:** `src/core/llm_factory.py`, `src/agents/base/base_agent.py`

- [ ] **Improve error responses**
  - Add structured error responses with error codes
  - Implement proper exception hierarchy
  - Add user-friendly error messages
  - Log errors with proper context
  - **Files:** `src/core/exceptions.py`, `src/api/middleware.py`

### 8. Testing Coverage
- [ ] **Implement unit tests for specialist agents**
  - Test IncidentTriageAgent
  - Test ThreatHuntingAgent
  - Test AnomalyInvestigationAgent
  - Test ComplianceAuditorAgent
  - Test VulnerabilityPrioritizationAgent
  - Test SecurityKnowledgeAgent with RAG
  - Test ReconOrchestratorAgent
  - **Files:** `tests/unit/test_agents/` (create test files)

- [ ] **Implement integration tests for graphs**
  - Test main_graph routing
  - Test security_ops_graph workflows
  - Test threat_intel_graph workflows
  - Test governance_graph workflows
  - Test state persistence across graph executions
  - **Files:** `tests/integration/test_graphs/` (create test files)

- [ ] **Complete end-to-end workflow tests** - [test_workflows.py:3](tests/e2e/test_workflows.py#L3)
  - Test complete incident response workflow
  - Test threat hunting workflow
  - Test compliance audit workflow
  - Test multi-team collaboration scenarios
  - **Files:** `tests/e2e/test_workflows.py`

### 9. Session Management
- [ ] **Implement session persistence and recovery**
  - Save conversation history to database
  - Enable session resumption from checkpoints
  - Add session listing and management endpoints
  - Implement session timeout and cleanup
  - **Files:** `src/services/agent_service.py`, `src/api/v1/agents.py`

---

## 🔵 Low Priority (P3)

Nice-to-have features and optimizations.

### 10. Real-time Features
- [ ] **Enhance WebSocket streaming**
  - Implement streaming for all agent types
  - Add progress indicators for long-running tasks
  - Support streaming of intermediate results
  - Add connection management and reconnection
  - **Files:** `src/api/v1/websocket.py`

### 11. Rate Limiting & Security
- [ ] **Implement rate limiting**
  - Add Redis-based rate limiter
  - Configure per-endpoint rate limits
  - Add user-based rate limiting
  - Implement graceful degradation
  - **Files:** `src/api/middleware.py`

- [ ] **Add input validation and sanitization**
  - Validate all API inputs with Pydantic
  - Sanitize user inputs to prevent injection
  - Add request size limits
  - Implement query complexity limits for graph execution
  - **Files:** `src/api/schemas/`, `src/utils/validators.py`

### 12. Monitoring & Observability
- [ ] **Add monitoring and metrics**
  - Implement Prometheus metrics export
  - Track agent execution times
  - Track LLM token usage
  - Monitor database connection pool
  - Add custom business metrics
  - **Files:** `src/utils/metrics.py`, `src/api/v1/health.py`

- [ ] **Enhance logging**
  - Add correlation IDs for request tracing
  - Implement log aggregation support
  - Add performance profiling logs
  - Configure log levels per environment
  - **Files:** `src/utils/logging.py`

---

## 📋 Quick Reference: Files with TODOs

| File | Line | Description |
|------|------|-------------|
| [src/db/models.py](src/db/models.py#L27) | 27 | Implement actual database models |
| [src/services/knowledge_service.py](src/services/knowledge_service.py#L11) | 11 | Initialize vector store (Chroma) |
| [src/services/knowledge_service.py](src/services/knowledge_service.py#L22) | 22 | Implement document embedding and storage |
| [src/services/knowledge_service.py](src/services/knowledge_service.py#L36) | 36 | Implement semantic search |
| [src/services/knowledge_service.py](src/services/knowledge_service.py#L49) | 49 | Implement context retrieval |
| [tests/e2e/test_workflows.py](tests/e2e/test_workflows.py#L3) | 3 | Implement end-to-end tests |
| [scripts/seed_data.py](scripts/seed_data.py#L6) | 6 | Implement knowledge base seeding |
| [scripts/seed_data.py](scripts/seed_data.py#L13) | 13 | Implement user seeding |

---

## 🚀 Recommended Implementation Order

### Phase 1: Core Infrastructure (Week 1-2)
1. Add PostgreSQL to docker-compose.yml
2. Implement database models
3. ✅ Update tests to use local databases ⭐ **COMPLETED**
4. Complete KnowledgeService implementation

### Phase 2: Multi-Agent Integration (Week 2-3)
5. ✅ Integrate team graphs into main supervisor **COMPLETED**
6. ✅ Implement full graph-based routing **COMPLETED**
7. Add missing specialist agent endpoints
8. Implement session management

### Phase 3: Testing & Reliability (Week 3-4)
9. Implement unit tests for all agents
10. Implement integration tests for graphs
11. Complete end-to-end workflow tests
12. Add retry logic and error handling

### Phase 4: Production Readiness (Week 4-5)
13. Implement proper authentication system
14. Add rate limiting and security features
15. Enhance monitoring and metrics
16. Complete data seeding scripts

---

## 📊 Progress Tracker

- **Critical (P0):** 2/3 complete (67%) ✅
  - ✅ Multi-Agent Orchestration
  - ✅ Testing Infrastructure
  - ⏳ Database Integration (in progress)
- **High (P1):** 0/3 complete (0%)
- **Medium (P2):** 0/3 complete (0%)
- **Low (P3):** 0/3 complete (0%)

**Overall:** 2/12 tasks complete (17%)

---

## 🔗 Related Documentation

- [README.md](README.md) - Project overview and setup
- [ARCHITECTURE_REDESIGN_REPORT.md](ARCHITECTURE_REDESIGN_REPORT.md) - Architecture details
- [FIXES_APPLIED.md](FIXES_APPLIED.md) - Previously completed fixes
- [docs/agent_guide.md](docs/agent_guide.md) - Agent development guide
- [docs/deployment.md](docs/deployment.md) - Deployment instructions

---

## 📝 Notes

- All TODOs marked with ⭐ are user-requested features
- File references use markdown links for easy navigation in VSCode
- Priority levels: P0 (Critical) → P1 (High) → P2 (Medium) → P3 (Low)
- Each task includes affected files for context

---

**Ready to start?** Begin with Phase 1 tasks to establish the core infrastructure!
