"""WebSocket endpoints for streaming responses."""

import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.agents.specialists.anomaly_investigation import AnomalyInvestigationAgent
from src.agents.specialists.compliance_auditor import ComplianceAuditorAgent
from src.agents.specialists.incident_triage import IncidentTriageAgent
from src.agents.specialists.recon_orchestrator import ReconOrchestratorAgent
from src.agents.specialists.security_knowledge import SecurityKnowledgeAgent
from src.agents.specialists.threat_hunting import ThreatHuntingAgent
from src.agents.specialists.vulnerability_prioritization import (
    VulnerabilityPrioritizationAgent,
)
from src.core.llm_factory import LLMFactory

router = APIRouter()

# Agent registry for name-based lookup
AGENT_REGISTRY = {
    "incident_triage": IncidentTriageAgent,
    "threat_hunting": ThreatHuntingAgent,
    "security_knowledge": SecurityKnowledgeAgent,
    "anomaly_investigation": AnomalyInvestigationAgent,
    "compliance_auditor": ComplianceAuditorAgent,
    "recon_orchestrator": ReconOrchestratorAgent,
    "vulnerability_prioritization": VulnerabilityPrioritizationAgent,
}


@router.websocket("/ws/agent/{agent_name}")
async def agent_websocket(websocket: WebSocket, agent_name: str):
    """
    WebSocket endpoint for streaming agent responses.

    The client should send a JSON message with:
    {
        "query": "User query",
        "context": {"key": "value"},  // optional
        "session_id": "session_123"   // optional
    }

    The server will stream back JSON messages with:
    {
        "type": "start|chunk|end|error",
        "content": "...",
        "metadata": {...}
    }

    Args:
        websocket: WebSocket connection
        agent_name: Name of the agent to execute
    """
    await websocket.accept()

    try:
        # Validate agent name
        if agent_name not in AGENT_REGISTRY:
            await websocket.send_json({
                "type": "error",
                "content": f"Unknown agent: {agent_name}",
                "available_agents": list(AGENT_REGISTRY.keys())
            })
            await websocket.close()
            return

        # Send acknowledgment
        await websocket.send_json({
            "type": "connected",
            "agent": agent_name,
            "message": "Connected to agent. Send your query."
        })

        # Wait for query from client
        data = await websocket.receive_text()
        try:
            request_data = json.loads(data)
        except json.JSONDecodeError:
            await websocket.send_json({
                "type": "error",
                "content": "Invalid JSON format"
            })
            await websocket.close()
            return

        query = request_data.get("query")
        context = request_data.get("context", {})
        session_id = request_data.get("session_id")

        if not query:
            await websocket.send_json({
                "type": "error",
                "content": "Missing 'query' field in request"
            })
            await websocket.close()
            return

        # Send start message
        await websocket.send_json({
            "type": "start",
            "content": f"Processing query with {agent_name}...",
            "metadata": {"agent": agent_name, "session_id": session_id}
        })

        # Initialize LLM and agent
        llm = LLMFactory.get_default_llm()
        agent_class = AGENT_REGISTRY[agent_name]
        agent = agent_class(llm)

        # Get prompt template
        prompt = ChatPromptTemplate.from_template(agent.get_prompt_template())

        # Create streaming chain
        chain = prompt | llm | StrOutputParser()

        # Prepare input variables based on agent context
        input_vars = {"query": query}
        if context:
            input_vars.update(context)

        # Stream response
        full_response = ""
        async for chunk in chain.astream(input_vars):
            full_response += chunk
            await websocket.send_json({
                "type": "chunk",
                "content": chunk
            })

        # Send completion message
        await websocket.send_json({
            "type": "end",
            "content": "Response complete",
            "metadata": {
                "agent": agent_name,
                "total_length": len(full_response),
                "session_id": session_id
            }
        })

    except WebSocketDisconnect:
        # Client disconnected
        pass
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "content": str(e)
            })
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass
