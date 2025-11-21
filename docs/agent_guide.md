# Agent Development Guide

## Overview

This guide explains how to add new agents to the GuardianEye system.

## Agent Types

### Specialist Agents

Specialist agents perform specific security tasks:
- Incident Triage
- Anomaly Investigation
- Vulnerability Prioritization
- Threat Hunting
- Reconnaissance Orchestration
- Compliance Auditing
- Security Knowledge Q&A

### Supervisor Agents

Supervisor agents coordinate specialist agents:
- Main Supervisor
- Security Operations Supervisor
- Threat Intelligence Supervisor
- Governance Supervisor

## Adding a New Specialist Agent

### Step 1: Create Agent File

Create a new file in `src/agents/specialists/`:

```python
# src/agents/specialists/my_agent.py

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.agents.base.base_agent import AgentInput, AgentOutput, BaseAgent


class MyAgent(BaseAgent):
    """Description of what this agent does."""

    def __init__(self, llm):
        super().__init__(llm, name="my_agent")
        self.parser = StrOutputParser()

    def get_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", "Your system prompt here"),
            ("user", "{query}")
        ])

    async def process(self, input_data: AgentInput) -> AgentOutput:
        chain = self.get_prompt_template() | self.llm | self.parser
        response = await chain.ainvoke({"query": input_data.query})

        return AgentOutput(
            result=response,
            metadata={"agent": self.name}
        )
```

### Step 2: Register Agent

Add to `src/config/agent_registry.py`:

```python
class AgentType(str, Enum):
    # ... existing agents
    MY_AGENT = "my_agent"
```

### Step 3: Add to Team

Update team mapping in `agent_registry.py`:

```python
TEAM_AGENTS_MAPPING = {
    TeamType.SECURITY_OPS: [
        # ... existing agents
        AgentType.MY_AGENT,
    ],
}
```

### Step 4: Create API Endpoint

Add endpoint in `src/api/v1/agents.py`:

```python
@router.post("/my-agent", response_model=AgentResponse)
async def run_my_agent(request: AgentRequest):
    # Implementation
    pass
```

### Step 5: Write Tests

Create tests in `tests/unit/test_agents/`:

```python
# tests/unit/test_agents/test_my_agent.py

def test_my_agent():
    # Test implementation
    pass
```

## Best Practices

1. **Clear Purpose**: Each agent should have a single, well-defined purpose
2. **Type Safety**: Use Pydantic models for all inputs and outputs
3. **Error Handling**: Handle exceptions gracefully
4. **Logging**: Add appropriate logging for debugging
5. **Testing**: Write comprehensive tests
6. **Documentation**: Document what the agent does and how to use it

## Prompt Engineering Tips

1. Be specific about the agent's role
2. Provide clear output format requirements
3. Include examples when helpful
4. Use system prompts for persistent instructions
5. Test with various inputs

## Example: Incident Triage Agent

See `src/agents/specialists/incident_triage.py` for a complete example.
