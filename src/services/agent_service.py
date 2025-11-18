"""Agent execution service."""

import time
import uuid
from typing import Any
from langchain_core.messages import HumanMessage

from src.agents.graphs.main_graph import create_main_graph
from src.core.state import GuardianEyeState
from src.core.checkpointer import get_checkpointer
from src.db.vector_store import get_vector_store


class AgentService:
    """Service for executing multi-agent workflows."""

    def __init__(self):
        """Initialize agent service."""
        self.graph = None
        self.checkpointer = None

    async def initialize(self):
        """Initialize the agent graph and checkpointer."""
        if self.graph is None:
            self.graph = create_main_graph()
        if self.checkpointer is None:
            self.checkpointer = await get_checkpointer()

    async def execute_query(
        self,
        query: str,
        user_id: str = "default_user",
        session_id: str | None = None,
        context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Execute a query through the multi-agent system.

        Args:
            query: User query
            user_id: User identifier
            session_id: Session identifier for state persistence
            context: Additional context

        Returns:
            Execution result with metadata
        """
        await self.initialize()

        # Generate session ID if not provided
        if session_id is None:
            session_id = str(uuid.uuid4())

        # Initialize state
        initial_state: GuardianEyeState = {
            "messages": [HumanMessage(content=query)],
            "user_id": user_id,
            "session_id": session_id,
            "current_team": None,
            "current_agent": None,
            "next_action": None,
            "intermediate_results": context or {},
            "final_result": None,
            "execution_path": [],
            "tool_calls": [],
            "total_tokens": 0,
            "start_time": time.time()
        }

        # Add vector store to context for RAG
        try:
            vector_store = get_vector_store()
            initial_state["intermediate_results"]["vector_store"] = vector_store
        except Exception as e:
            print(f"Warning: Could not initialize vector store: {e}")

        # Execute graph
        config = {
            "configurable": {
                "thread_id": session_id,
                "checkpoint_ns": user_id
            }
        }

        try:
            # Run the graph
            result = await self.graph.ainvoke(initial_state, config=config)

            # Calculate execution time
            execution_time = time.time() - result.get("start_time", time.time())

            return {
                "result": result.get("final_result", "No result generated"),
                "execution_path": result.get("execution_path", []),
                "session_id": session_id,
                "execution_time": execution_time,
                "metadata": {
                    "user_id": user_id,
                    "team": result.get("current_team"),
                    "agent": result.get("current_agent"),
                    "tokens": result.get("total_tokens", 0)
                }
            }

        except Exception as e:
            return {
                "result": f"Error executing query: {str(e)}",
                "error": str(e),
                "execution_path": [],
                "session_id": session_id,
                "execution_time": 0,
                "metadata": {}
            }

    async def get_session_history(self, session_id: str) -> list[dict]:
        """Get conversation history for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of messages in the session
        """
        # This would query the checkpointer for session history
        # Implementation depends on checkpointer capabilities
        return []
