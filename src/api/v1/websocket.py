"""WebSocket endpoints for streaming responses (placeholder)."""

from fastapi import APIRouter, WebSocket

router = APIRouter()


@router.websocket("/ws/agent/{agent_name}")
async def agent_websocket(websocket: WebSocket, agent_name: str):
    """
    WebSocket endpoint for streaming agent responses.

    Args:
        websocket: WebSocket connection
        agent_name: Name of the agent to execute
    """
    await websocket.accept()

    try:
        # TODO: Implement actual streaming
        await websocket.send_json({
            "message": "WebSocket streaming not yet implemented",
            "agent": agent_name
        })
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()
