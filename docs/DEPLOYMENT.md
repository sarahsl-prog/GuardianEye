# GuardianEye Deployment Guide

This guide covers deploying GuardianEye to staging and production environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Monitoring & Logging](#monitoring--logging)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Services
- PostgreSQL 16+ (for state persistence)
- Redis 7+ (for caching and sessions)
- Ollama (optional, for local LLM)
- Docker 24+ (for containerized deployment)
- Kubernetes 1.28+ (for K8s deployment)

### API Keys (Optional)
- OpenAI API key (if using GPT models)
- Anthropic API key (if using Claude)
- Google API key (if using Gemini)

## Environment Configuration

### Staging Environment

Create `.env.staging`:

```bash
# Application
APP_ENV=staging
APP_NAME=GuardianEye
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# LLM Provider
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://ollama:11434

# Database
POSTGRES_URL=postgresql+asyncpg://guardianeye:secure_password@postgres:5432/guardianeye_staging
REDIS_URL=redis://redis:6379/0

# Security
JWT_SECRET_KEY=staging-secret-key-change-me
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["https://staging.guardianeye.com"]
```

### Production Environment

Create `.env.production`:

```bash
# Application
APP_ENV=production
APP_NAME=GuardianEye
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=WARNING

# LLM Provider
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-ant-production-key

# Database (use managed services)
POSTGRES_URL=postgresql+asyncpg://user:pass@rds-endpoint:5432/guardianeye_prod
REDIS_URL=redis://elasticache-endpoint:6379/0

# Security
JWT_SECRET_KEY=production-secret-key-very-secure
ACCESS_TOKEN_EXPIRE_MINUTES=15

# CORS
CORS_ORIGINS=["https://guardianeye.com","https://app.guardianeye.com"]
```

## Docker Deployment

### Build Image

```bash
# Build production image
docker build -t guardianeye:2.0.0 .
docker tag guardianeye:2.0.0 guardianeye:latest

# Push to registry (optional)
docker tag guardianeye:2.0.0 your-registry/guardianeye:2.0.0
docker push your-registry/guardianeye:2.0.0
```

### Deploy with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  app:
    image: your-registry/guardianeye:2.0.0
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    restart: always
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Kubernetes Deployment

### 1. Create Namespace

```bash
kubectl create namespace guardianeye-prod
kubectl config set-context --current --namespace=guardianeye-prod
```

### 2. Create Secrets

```bash
# Create database secrets
kubectl create secret generic guardianeye-secrets \
  --from-literal=postgres_url="postgresql+asyncpg://user:pass@postgres:5432/guardianeye" \
  --from-literal=redis_url="redis://redis:6379/0" \
  --from-literal=jwt_secret="your-jwt-secret" \
  --from-literal=openai_api_key="" \
  --from-literal=anthropic_api_key="sk-ant-..."
```

### 3. Deploy PostgreSQL

```bash
kubectl apply -f k8s/postgres.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s
```

### 4. Deploy Redis

```bash
kubectl apply -f k8s/redis.yaml

# Verify
kubectl get pods -l app=redis
```

### 5. Deploy Application

```bash
kubectl apply -f k8s/deployment.yaml

# Check deployment
kubectl get deployments
kubectl get pods
kubectl get services
```

### 6. Verify Deployment

```bash
# Get service endpoint
kubectl get service guardianeye

# Test health check
kubectl port-forward service/guardianeye 8000:80
curl http://localhost:8000/api/v1/health
```

### 7. Scale Deployment

```bash
# Scale to 5 replicas
kubectl scale deployment guardianeye --replicas=5

# Auto-scaling (optional)
kubectl autoscale deployment guardianeye --min=3 --max=10 --cpu-percent=70
```

## Monitoring & Logging

### Health Checks

```bash
# Liveness check
curl http://your-domain/api/v1/health

# Readiness check
curl http://your-domain/api/v1/health/ready
```

### Application Logs

Docker:
```bash
# View logs
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app
```

Kubernetes:
```bash
# View logs from all pods
kubectl logs -l app=guardianeye --tail=100 -f

# View logs from specific pod
kubectl logs guardianeye-7d9b8c6f5-abc12 -f
```

### Metrics Collection

Add Prometheus monitoring:

```yaml
# k8s/monitoring.yaml
apiVersion: v1
kind: Service
metadata:
  name: guardianeye-metrics
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8000"
    prometheus.io/path: "/metrics"
spec:
  selector:
    app: guardianeye
  ports:
  - port: 8000
    targetPort: 8000
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

```bash
# Check PostgreSQL status
kubectl exec -it postgres-0 -- psql -U guardianeye -d guardianeye -c "SELECT 1;"

# Check connection string
kubectl get secret guardianeye-secrets -o jsonpath='{.data.postgres_url}' | base64 -d
```

#### 2. Redis Connection Errors

```bash
# Test Redis connection
kubectl exec -it <redis-pod> -- redis-cli ping

# Check Redis service
kubectl get service redis-service
```

#### 3. LLM Provider Errors

```bash
# Check API keys
kubectl get secret guardianeye-secrets -o jsonpath='{.data.openai_api_key}' | base64 -d

# Test Ollama connection
curl http://ollama:11434/api/tags
```

#### 4. Pod Crashes

```bash
# Check pod status
kubectl describe pod <pod-name>

# View crash logs
kubectl logs <pod-name> --previous
```

### Performance Tuning

#### Increase Replicas

```bash
kubectl scale deployment guardianeye --replicas=10
```

#### Resource Limits

Update `k8s/deployment.yaml`:

```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

#### Database Connection Pool

Update `.env`:

```bash
POSTGRES_POOL_SIZE=20
POSTGRES_MAX_OVERFLOW=40
```

## Backup & Recovery

### Database Backup

```bash
# Backup PostgreSQL
kubectl exec postgres-0 -- pg_dump -U guardianeye guardianeye > backup.sql

# Restore
kubectl exec -i postgres-0 -- psql -U guardianeye guardianeye < backup.sql
```

### Vector Store Backup

```bash
# Backup Chroma data
kubectl cp <pod-name>:/app/data/chroma ./chroma-backup

# Restore
kubectl cp ./chroma-backup <pod-name>:/app/data/chroma
```

## Security Hardening

### 1. Use Secrets Manager

AWS Secrets Manager example:

```bash
# Store secrets in AWS
aws secretsmanager create-secret --name guardianeye/jwt-secret --secret-string "your-secret"

# Reference in pod
apiVersion: v1
kind: Pod
metadata:
  name: guardianeye
spec:
  serviceAccountName: guardianeye-sa
  containers:
  - name: guardianeye
    image: guardianeye:2.0.0
    env:
    - name: JWT_SECRET_KEY
      valueFrom:
        secretKeyRef:
          name: guardianeye-secrets
          key: jwt_secret
```

### 2. Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: guardianeye-policy
spec:
  podSelector:
    matchLabels:
      app: guardianeye
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 8000
```

### 3. TLS/SSL

Use cert-manager for automatic TLS:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

## Rollback

### Docker Compose

```bash
# Tag current as backup
docker tag guardianeye:latest guardianeye:backup

# Revert to previous version
docker-compose down
docker-compose up -d
```

### Kubernetes

```bash
# View deployment history
kubectl rollout history deployment guardianeye

# Rollback to previous version
kubectl rollout undo deployment guardianeye

# Rollback to specific revision
kubectl rollout undo deployment guardianeye --to-revision=2
```

## Production Checklist

- [ ] All secrets configured in secret manager
- [ ] Database backups automated
- [ ] Monitoring and alerting configured
- [ ] Health checks passing
- [ ] TLS/SSL certificates valid
- [ ] Logging aggregation set up
- [ ] Auto-scaling configured
- [ ] Resource limits defined
- [ ] Network policies applied
- [ ] Disaster recovery plan documented

---

For additional support, contact the infrastructure team or open an issue.
