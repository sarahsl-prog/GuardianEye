# Deployment Guide

## Development Deployment

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Git

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/your-org/GuardianEye.git
cd GuardianEye
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Update `.env` with your configuration:
   - Set `LLM_PROVIDER` (ollama, openai, anthropic, google)
   - Add API keys if using cloud providers
   - Configure database URLs if needed

4. Start services:
```bash
docker-compose up -d
```

5. Install Python dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

6. Setup database:
```bash
python scripts/setup_db.py
```

7. Run the application:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

8. Access the API:
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

## Production Deployment

### Option 1: Docker Container

1. Build the image:
```bash
docker build -t guardianeye:latest .
```

2. Run the container:
```bash
docker run -d \
  --name guardianeye \
  -p 8000:8000 \
  --env-file .env \
  guardianeye:latest
```

### Option 2: Kubernetes

1. Create ConfigMap for environment variables
2. Create Deployment manifest
3. Create Service for load balancing
4. Apply manifests:
```bash
kubectl apply -f k8s/
```

### Option 3: Cloud Platforms

**AWS**:
- Use ECS or EKS for container orchestration
- RDS for PostgreSQL
- ElastiCache for Redis
- EFS for persistent storage

**GCP**:
- Use GKE or Cloud Run
- Cloud SQL for PostgreSQL
- Memorystore for Redis

**Azure**:
- Use AKS or Container Instances
- Azure Database for PostgreSQL
- Azure Cache for Redis

## Environment Variables

See `.env.example` for all available configuration options.

Critical variables for production:
- `APP_ENV=production`
- `JWT_SECRET_KEY` - Change to a secure random value
- `POSTGRES_URL` - Production database URL
- `REDIS_URL` - Production Redis URL
- API keys for your chosen LLM provider

## Monitoring

### Health Checks

- `/health` - Basic health check
- `/api/v1/ready` - Readiness probe
- `/api/v1/live` - Liveness probe

### Logging

Logs are output to stdout in JSON format. Configure log aggregation:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Datadog
- CloudWatch (AWS)
- Cloud Logging (GCP)

### Metrics

TODO: Implement Prometheus metrics endpoint

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **JWT Secret**: Use a strong random secret in production
3. **HTTPS**: Always use HTTPS in production
4. **Rate Limiting**: Implement rate limiting on API endpoints
5. **Authentication**: Enable authentication for all endpoints
6. **Database**: Use strong passwords and encrypted connections

## Scaling

### Horizontal Scaling

The application is stateless (state is in PostgreSQL), so you can:
- Run multiple instances behind a load balancer
- Use auto-scaling groups
- Scale based on CPU/memory usage

### Database Scaling

- Use PostgreSQL read replicas for read-heavy workloads
- Use connection pooling (pgBouncer)
- Consider partitioning for large datasets

### Caching

- Use Redis for caching LLM responses
- Implement request deduplication
- Cache agent results with appropriate TTL

## Backup and Recovery

1. **Database**: Regular PostgreSQL backups
2. **Vector Store**: Backup Chroma data directory
3. **Configuration**: Keep `.env` files in secure backup

## Troubleshooting

### Common Issues

1. **LLM Connection Failed**:
   - Check API keys
   - Verify network connectivity
   - Check LLM provider status

2. **Database Connection Failed**:
   - Verify PostgreSQL is running
   - Check connection string
   - Verify network access

3. **High Latency**:
   - Check LLM response times
   - Enable caching
   - Optimize prompts
   - Consider faster LLM models
