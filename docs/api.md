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

**GET** `/health`

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
