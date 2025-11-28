# Multi-Agent Orchestration Implementation Plan

**Date:** 2024-11-28
**Task:** #1 Multi-Agent Orchestration (P0 - Critical)
**Status:** Planning Complete

---

## 🎯 Objectives

1. **Integrate team graphs into main supervisor** - Replace placeholder team nodes with actual subgraph calls
2. **Implement full graph-based routing** - Replace direct agent execution with main graph invocation

---

## 📊 Current State Analysis

### What Exists ✅

#### Main Graph (`src/agents/graphs/main_graph.py`)
- ✅ Main supervisor node that routes to teams (line 13-31)
- ✅ Routing logic via `route_to_team()` (line 76-83)
- ✅ Proper graph structure with conditional edges
- ❌ **Team nodes are PLACEHOLDERS** (lines 34-73) - just add messages, don't execute subgraphs

#### Team Graphs (All Complete!)
- ✅ **Security Ops Graph** (`security_ops_graph.py`)
  - 3 agents: Incident Triage, Anomaly Investigation, Vulnerability Prioritization
  - Smart routing via `route_security_ops()`
  - `create_security_ops_graph()` returns compiled graph

- ✅ **Threat Intel Graph** (`threat_intel_graph.py`)
  - 2 agents: Threat Hunting, Recon Orchestrator
  - Smart routing via `route_threat_intel()`
  - `create_threat_intel_graph()` returns compiled graph

- ✅ **Governance Graph** (`governance_graph.py`)
  - 2 agents: Compliance Auditor, Security Knowledge (with RAG)
  - Smart routing via `route_governance()`
  - `create_governance_graph()` returns compiled graph

#### API Layer (`src/api/v1/agents.py`)
- ❌ `/execute` endpoint directly calls `IncidentTriageAgent` (line 50)
- ❌ TODO comment acknowledges this needs fixing (line 49)
- ✅ Individual agent endpoints exist
- ❌ No use of main graph or routing

#### Agent Service (`src/services/agent_service.py`)
- ✅ Already imports and uses `create_main_graph()` (line 8, 25)
- ✅ Proper state initialization with `GuardianEyeState`
- ✅ Executes graph with `ainvoke()`
- ❌ **NOT currently used by API endpoints** - this is the key issue!

---

## 🏗️ Implementation Strategy

### Part 1: Integrate Team Subgraphs into Main Graph

**File:** `src/agents/graphs/main_graph.py`

**Current Placeholder Pattern:**
```python
async def security_ops_team_node(state: GuardianEyeState):
    """Security operations team node."""
    # Placeholder - will be expanded with actual team graph
    state["execution_path"].append("security_ops_team")
    state["final_result"] = "Security Operations Team processing..."
    return state
```

**New Subgraph Integration Pattern:**
```python
async def security_ops_team_node(state: GuardianEyeState):
    """Security operations team node - executes security ops subgraph."""
    from src.agents.graphs.security_ops_graph import create_security_ops_graph

    # Create and execute the security ops subgraph
    security_ops_graph = create_security_ops_graph()

    # Execute subgraph with current state
    result_state = await security_ops_graph.ainvoke(state)

    # Update execution path
    result_state["execution_path"].append("security_ops_team")

    return result_state
```

**Changes Required:**
1. Import team graph creators at top of file
2. Replace 3 placeholder functions with actual subgraph invocations
3. Each team node will:
   - Create compiled team graph
   - Execute it with current state
   - Return updated state with results

**Benefits:**
- ✅ Hierarchical execution: Main → Team → Specialist
- ✅ State flows through entire system
- ✅ Each team graph handles its own routing
- ✅ Maintains execution path for debugging

---

### Part 2: Update API to Use AgentService

**File:** `src/api/v1/agents.py`

**Current Direct Agent Call:**
```python
@router.post("/execute", response_model=AgentResponse)
async def execute_agent(request: AgentRequest, ...):
    llm = LLMFactory.get_default_llm()
    # TODO: Implement full graph-based routing with main supervisor
    agent = IncidentTriageAgent(llm)  # ❌ Directly calls one agent
    result = await agent.process(agent_input)
    return AgentResponse(...)
```

**New Graph-Based Routing:**
```python
@router.post("/execute", response_model=AgentResponse)
async def execute_agent(request: AgentRequest, ...):
    from src.services.agent_service import AgentService

    # Use agent service for full graph orchestration
    service = AgentService()
    result = await service.execute_query(
        query=request.query,
        user_id=user.get("user_id", "anonymous") if user else "anonymous",
        session_id=request.session_id,
        context=request.context
    )

    return AgentResponse(
        result=result["result"],
        agent_name=result["metadata"].get("agent", "multi-agent"),
        execution_time=result["execution_time"],
        metadata=result["metadata"],
        session_id=result["session_id"],
        execution_path=result["execution_path"]
    )
```

**Benefits:**
- ✅ Intelligent routing via main supervisor
- ✅ Multi-step workflows possible
- ✅ Full execution path tracking
- ✅ State persistence with checkpointer
- ✅ Proper team-based organization

---

## 🧪 Testing Strategy

### Unit Tests

**File:** `tests/unit/test_graphs/test_main_graph.py` (NEW)

```python
async def test_main_graph_routes_to_security_ops(mock_llm):
    """Test main graph routes incident queries to security ops team."""
    # Given: A security incident query
    # When: Main graph executes
    # Then: Routes to security_ops_team and executes incident triage

async def test_main_graph_routes_to_threat_intel(mock_llm):
    """Test main graph routes threat queries to threat intel team."""

async def test_main_graph_routes_to_governance(mock_llm):
    """Test main graph routes compliance queries to governance team."""

async def test_security_ops_subgraph_integration(mock_llm):
    """Test security ops subgraph executes within main graph."""
    # Verify subgraph is called and returns proper state

async def test_execution_path_tracking(mock_llm):
    """Test execution path is properly tracked through hierarchy."""
    # Verify path includes: main_supervisor → team → specialist agent
```

### Integration Tests

**File:** `tests/integration/test_graphs/test_full_orchestration.py` (NEW)

```python
async def test_end_to_end_incident_triage(client, mock_llm):
    """Test full workflow from API to incident triage via graph."""
    response = client.post("/api/v1/agents/execute", json={
        "query": "Analyze this security incident: failed logins from 192.168.1.100"
    })
    assert response.status_code == 200
    data = response.json()
    assert "security_ops_team" in data["execution_path"]
    assert "incident_triage" in data["execution_path"]

async def test_end_to_end_threat_hunting(client, mock_llm):
    """Test full workflow from API to threat hunting via graph."""

async def test_end_to_end_compliance_audit(client, mock_llm):
    """Test full workflow from API to compliance audit via graph."""
```

### Workflow Tests

**File:** `tests/e2e/test_workflows.py` (UPDATE)

```python
async def test_complete_incident_response_workflow(mock_llm):
    """Test complete incident response from triage to resolution."""
    # This test will now work with actual graph execution

async def test_multi_step_threat_investigation(mock_llm):
    """Test multi-step workflow across teams."""
    # Test that can route to multiple teams in sequence
```

---

## 📝 Implementation Steps

### Step 1: Update Main Graph with Subgraph Integration
1. Open `src/agents/graphs/main_graph.py`
2. Add imports for team graph creators
3. Replace `security_ops_team_node()` with subgraph invocation
4. Replace `threat_intel_team_node()` with subgraph invocation
5. Replace `governance_team_node()` with subgraph invocation
6. Test that graphs compile without errors

### Step 2: Update API to Use AgentService
1. Open `src/api/v1/agents.py`
2. Update `/execute` endpoint to use `AgentService`
3. Extract user_id from auth context properly
4. Map service response to `AgentResponse` schema
5. Keep individual agent endpoints (for backward compatibility)

### Step 3: Create Unit Tests
1. Create `tests/unit/test_graphs/` directory
2. Create `test_main_graph.py` with routing tests
3. Create `test_subgraph_integration.py` for integration tests
4. Mock LLM responses for predictable routing
5. Verify execution paths

### Step 4: Create Integration Tests
1. Create `tests/integration/test_graphs/` directory (if not exists)
2. Create `test_full_orchestration.py`
3. Test API → AgentService → Main Graph → Team Graph → Agent
4. Verify responses and execution paths
5. Test error handling

### Step 5: Update Documentation
1. Update `TODO.md` - mark task #1 as complete
2. Create `MULTI_AGENT_ORCHESTRATION.md` - Architecture documentation
3. Update `README.md` - Explain multi-agent routing
4. Add code comments explaining subgraph pattern

---

## 🎯 Success Criteria

### Functional
- ✅ Main graph successfully invokes team subgraphs
- ✅ Team subgraphs execute their specialist agents
- ✅ State flows correctly through hierarchy
- ✅ Execution path shows complete routing
- ✅ API `/execute` endpoint uses graph routing
- ✅ Intelligent routing based on query content

### Technical
- ✅ No placeholder functions remain
- ✅ All team graphs integrated
- ✅ AgentService used by API
- ✅ Proper error handling
- ✅ State persistence works

### Testing
- ✅ Unit tests pass (15+ new tests)
- ✅ Integration tests pass (5+ new tests)
- ✅ Existing tests still pass (22+ tests)
- ✅ Coverage > 50%

### Documentation
- ✅ Architecture documented
- ✅ Code comments added
- ✅ TODO.md updated
- ✅ Examples provided

---

## 🚀 Execution Timeline

1. **Main Graph Integration** - 30 minutes
   - Update team node functions
   - Add imports
   - Test compilation

2. **API Update** - 20 minutes
   - Update `/execute` endpoint
   - Test with curl/Postman
   - Verify responses

3. **Unit Tests** - 45 minutes
   - Create test files
   - Write 15+ unit tests
   - Mock LLM responses
   - Verify all pass

4. **Integration Tests** - 30 minutes
   - Create integration tests
   - Test full workflows
   - Verify execution paths

5. **Documentation** - 20 minutes
   - Update TODO.md
   - Create architecture doc
   - Add code comments

**Total Estimated Time:** ~2.5 hours

---

## ⚠️ Potential Challenges

### Challenge 1: State Compatibility
**Issue:** Subgraphs might expect different state structure
**Solution:** All team graphs use `GuardianEyeState` - already compatible!

### Challenge 2: Error Propagation
**Issue:** Errors in subgraphs might not bubble up properly
**Solution:** Add try/except in team nodes, update state with errors

### Challenge 3: Vector Store Context
**Issue:** Security Knowledge agent needs vector store in context
**Solution:** AgentService already adds vector_store to context (line 71-74)

### Challenge 4: Backward Compatibility
**Issue:** Individual agent endpoints might break
**Solution:** Keep them as-is, they don't need to change

---

## 📊 Expected Improvements

### Before (Current)
```
User → /execute → IncidentTriageAgent → Response
```
- ❌ No routing intelligence
- ❌ Always same agent
- ❌ No team organization
- ❌ Single-step only

### After (Implemented)
```
User → /execute → AgentService → Main Graph → Main Supervisor
                                     ↓
                          [Routes to appropriate team]
                                     ↓
                          Team Graph → Team Routing
                                     ↓
                         [Routes to specialist agent]
                                     ↓
                          Specialist Agent → Response
```
- ✅ Intelligent routing via LLM
- ✅ Hierarchical organization
- ✅ Multi-step workflows possible
- ✅ Full execution tracking
- ✅ State persistence
- ✅ Scalable architecture

---

## ✅ Plan Approval Checklist

Before proceeding with implementation:
- [x] Explored current codebase thoroughly
- [x] Identified all team graphs and their structure
- [x] Understood current API routing
- [x] Designed subgraph integration pattern
- [x] Planned API updates
- [x] Defined testing strategy
- [x] Documented success criteria
- [x] Estimated timeline

**Ready for implementation!**
