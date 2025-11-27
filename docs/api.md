# API Documentation

## Base URL

Development: `http://localhost:8000`
Production: `https://your-domain.com`

## Authentication

Currently, authentication is optional for development.

For production, include JWT token in Authorization header:
```
Authorization: Bearer <your-token>
```

## Endpoints

### Health Check

**GET** `/health` or **GET** `/api/v1/health`

Check API health status.

**Response**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "environment": "development",
  "llm_provider": "ollama"
}
```

### Readiness Check

**GET** `/api/v1/ready`

Kubernetes-style readiness probe that checks if all required services are available.

**Success Response (200)**:
```json
{
  "ready": true,
  "services": {
    "postgres": "healthy",
    "redis": "healthy",
    "llm": "healthy"
  }
}
```

**Failure Response (503)**:
```json
{
  "detail": {
    "ready": false,
    "services": {
      "postgres": "unhealthy: Connection failed",
      "redis": "healthy",
      "llm": "healthy"
    }
  }
}
```

**Use Cases**:
- Kubernetes readiness probes
- Load balancer health checks
- Service dependency monitoring
- Pre-deployment validation

### Liveness Check

**GET** `/api/v1/live`

Kubernetes-style liveness probe to verify the application is running.

**Response**:
```json
{
  "alive": true
}
```

### Execute Agent (Auto-Routing)

**POST** `/api/v1/agents/execute`

Execute an agent with automatic routing through the supervisor hierarchy.

**Request Body**:
```json
{
  "query": "Analyze this security alert",
  "context": {
    "alert_details": "Suspicious login from 192.168.1.1",
    "alert_severity": "high"
  },
  "session_id": "optional_session_id",
  "stream": false
}
```

**Response**:
```json
{
  "result": "Analysis result from the agent...",
  "agent_name": "incident_triage",
  "execution_time": 2.34,
  "tokens_used": 450,
  "metadata": {
    "severity": "high",
    "confidence": 0.95
  },
  "session_id": "optional_session_id",
  "execution_path": [
    "main_supervisor -> security_ops_team",
    "security_ops_team -> incident_triage"
  ]
}
```

### Execute Specific Agent

**POST** `/api/v1/agents/{agent_name}`

Execute a specific agent directly.

Available agents:
- `/api/v1/agents/incident-triage`
- `/api/v1/agents/threat-hunting`
- `/api/v1/agents/security-knowledge`
- (more agents available)

**Request/Response**: Same as `/execute` endpoint

### List Agents

**GET** `/api/v1/agents/list`

Get list of all available agents organized by team.

**Response**:
```json
{
  "security_ops_team": [
    "incident_triage",
    "anomaly_investigation",
    "vulnerability_prioritization"
  ],
  "threat_intel_team": [
    "threat_hunting",
    "recon_orchestrator"
  ],
  "governance_team": [
    "compliance_auditor",
    "security_knowledge"
  ]
}
```

### WebSocket Streaming

**WebSocket** `/api/v1/ws/agent/{agent_name}`

Stream agent responses in real-time via WebSocket connection.

**Available Agents**:
- `incident_triage`
- `threat_hunting`
- `security_knowledge`
- `anomaly_investigation`
- `compliance_auditor`
- `recon_orchestrator`
- `vulnerability_prioritization`

**Connection Flow**:

1. **Connect** to the WebSocket endpoint
2. **Receive** connection acknowledgment
3. **Send** query message
4. **Receive** streaming response chunks
5. **Receive** completion message

**Client Message Format**:
```json
{
  "query": "Analyze this security alert",
  "context": {
    "alert_details": "Suspicious login attempt",
    "severity": "high"
  },
  "session_id": "session_123"
}
```

**Server Message Types**:

**1. Connected**:
```json
{
  "type": "connected",
  "agent": "incident_triage",
  "message": "Connected to agent. Send your query."
}
```

**2. Start**:
```json
{
  "type": "start",
  "content": "Processing query with incident_triage...",
  "metadata": {
    "agent": "incident_triage",
    "session_id": "session_123"
  }
}
```

**3. Chunk** (multiple, streamed in real-time):
```json
{
  "type": "chunk",
  "content": "This is a piece of the response..."
}
```

**4. End**:
```json
{
  "type": "end",
  "content": "Response complete",
  "metadata": {
    "agent": "incident_triage",
    "total_length": 1234,
    "session_id": "session_123"
  }
}
```

**5. Error**:
```json
{
  "type": "error",
  "content": "Error description"
}
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error description",
  "error": "error_type"
}
```

### Common Status Codes

- `200` - Success
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (authentication required)
- `404` - Not Found
- `500` - Internal Server Error

## Interactive Documentation

Visit `/docs` for interactive Swagger UI documentation.
Visit `/redoc` for ReDoc documentation.

## Rate Limiting

TODO: Implement rate limiting

## Examples

### cURL Example

```bash
curl -X POST http://localhost:8000/api/v1/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are best practices for securing cloud infrastructure?",
    "context": {}
  }'
```

### Python Example

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/agents/execute",
    json={
        "query": "Analyze this security incident",
        "context": {
            "alert_details": "Multiple failed login attempts",
            "alert_severity": "medium"
        }
    }
)

result = response.json()
print(result["result"])
```

### JavaScript Example

```javascript
const response = await fetch('http://localhost:8000/api/v1/agents/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'Generate threat hunting hypotheses for ransomware',
    context: {}
  })
});

const data = await response.json();
console.log(data.result);
```

### WebSocket Python Example

```python
import asyncio
import json
import websockets

async def stream_agent_response():
    uri = "ws://localhost:8000/api/v1/ws/agent/incident_triage"

    async with websockets.connect(uri) as websocket:
        # Receive connection acknowledgment
        connected = await websocket.recv()
        print(f"Connected: {connected}")

        # Send query
        query = {
            "query": "Analyze this security alert",
            "context": {
                "alert_details": "Multiple failed login attempts from 192.168.1.100",
                "severity": "high"
            },
            "session_id": "example_session"
        }
        await websocket.send(json.dumps(query))

        # Receive streaming responses
        full_response = ""
        while True:
            message = await websocket.recv()
            data = json.loads(message)

            if data["type"] == "start":
                print(f"Processing: {data['content']}")
            elif data["type"] == "chunk":
                full_response += data["content"]
                print(data["content"], end="", flush=True)
            elif data["type"] == "end":
                print(f"\n\nComplete! Total length: {data['metadata']['total_length']}")
                break
            elif data["type"] == "error":
                print(f"Error: {data['content']}")
                break

asyncio.run(stream_agent_response())
```

### WebSocket JavaScript Example

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/agent/threat_hunting');

ws.onopen = () => {
  console.log('WebSocket connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'connected') {
    console.log('Agent connected:', data.agent);

    // Send query
    ws.send(JSON.stringify({
      query: 'Identify potential threat hunting opportunities',
      context: {},
      session_id: 'web_session_123'
    }));
  } else if (data.type === 'start') {
    console.log('Processing started...');
  } else if (data.type === 'chunk') {
    // Display streaming content in real-time
    process.stdout.write(data.content);
  } else if (data.type === 'end') {
    console.log('\n\nResponse complete!');
    ws.close();
  } else if (data.type === 'error') {
    console.error('Error:', data.content);
    ws.close();
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket disconnected');
};
```
