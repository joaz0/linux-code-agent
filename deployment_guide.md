# 🚀 Deployment Guide - Linux Code Agent

Guia completo para deployar o agent em diferentes ambientes.

---

## 📋 Índice

1. [Desenvolvimento Local](#desenvolvimento-local)
2. [Servidor Linux](#servidor-linux)
3. [Docker](#docker)
4. [Kubernetes](#kubernetes)
5. [Cloud Providers](#cloud-providers)
6. [Produção Checklist](#produção-checklist)

---

## 💻 Desenvolvimento Local

### Setup Rápido

```bash
cd ~/projeto/backend

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Dependências
pip install -r requirements.txt

# Configuração
cp .env.example .env
nano .env  # Editar API keys

# Rodar
python3 -m app.app
```

### Desenvolvimento com Hot Reload

```bash
# Uvicorn com auto-reload
uvicorn app.app:app --reload --host 127.0.0.1 --port 8000

# Ou com log detalhado
uvicorn app.app:app --reload --log-level debug
```

---

## 🖥️ Servidor Linux

### Ubuntu/Debian

#### 1. Preparar Sistema

```bash
# Atualizar sistema
sudo apt update
sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx

# Criar usuário dedicado
sudo useradd -m -s /bin/bash agentuser
sudo su - agentuser
```

#### 2. Deploy da Aplicação

```bash
# Clone
git clone <repo> /home/agentuser/agent
cd /home/agentuser/agent/backend

# Virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Dependências
pip install -r requirements.txt
pip install gunicorn

# Configuração
nano .env
# Configure API keys
```

#### 3. Systemd Service

```bash
sudo nano /etc/systemd/system/code-agent.service
```

```ini
[Unit]
Description=Linux Code Agent API
After=network.target

[Service]
Type=notify
User=agentuser
Group=agentuser
WorkingDirectory=/home/agentuser/agent/backend
Environment="PATH=/home/agentuser/agent/backend/venv/bin"
ExecStart=/home/agentuser/agent/backend/venv/bin/gunicorn \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/code-agent/access.log \
    --error-logfile /var/log/code-agent/error.log \
    app.app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Criar diretório de logs
sudo mkdir -p /var/log/code-agent
sudo chown agentuser:agentuser /var/log/code-agent

# Ativar service
sudo systemctl daemon-reload
sudo systemctl enable code-agent
sudo systemctl start code-agent
sudo systemctl status code-agent
```

#### 4. Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/code-agent
```

```nginx
server {
    listen 80;
    server_name agent.example.com;

    # Logs
    access_log /var/log/nginx/code-agent-access.log;
    error_log /var/log/nginx/code-agent-error.log;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (futuro)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/code-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 5. SSL com Let's Encrypt

```bash
# Instalar certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d agent.example.com

# Auto-renewal
sudo systemctl status certbot.timer
```

---

## 🐳 Docker

### Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

# Metadata
LABEL maintainer="seu@email.com"
LABEL version="0.1.0"

# Working directory
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY app/ ./app/

# Non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: code-agent-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - LLM_PROVIDER=${LLM_PROVIDER:-anthropic}
      - LLM_MODEL=${LLM_MODEL:-claude-sonnet-4-20250514}
    env_file:
      - .env
    volumes:
      - ./workspace:/workspace  # Workspace para agent
      - ./logs:/app/logs        # Logs persistentes
    networks:
      - agent-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Redis para cache (futuro)
  # redis:
  #   image: redis:7-alpine
  #   container_name: code-agent-redis
  #   restart: unless-stopped
  #   volumes:
  #     - redis-data:/data
  #   networks:
  #     - agent-network

  # PostgreSQL para persistência (futuro)
  # postgres:
  #   image: postgres:15-alpine
  #   container_name: code-agent-db
  #   restart: unless-stopped
  #   environment:
  #     POSTGRES_DB: codeagent
  #     POSTGRES_USER: agent
  #     POSTGRES_PASSWORD: ${DB_PASSWORD}
  #   volumes:
  #     - postgres-data:/var/lib/postgresql/data
  #   networks:
  #     - agent-network

networks:
  agent-network:
    driver: bridge

# volumes:
#   redis-data:
#   postgres-data:
```

### Build e Run

```bash
# Build
docker-compose build

# Run
docker-compose up -d

# Logs
docker-compose logs -f api

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build
```

### Docker sem Compose

```bash
# Build
docker build -t code-agent:latest .

# Run
docker run -d \
  --name code-agent \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -v $(pwd)/workspace:/workspace \
  code-agent:latest

# Logs
docker logs -f code-agent

# Stop
docker stop code-agent
docker rm code-agent
```

---

## ☸️ Kubernetes

### Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: code-agent
  namespace: default
  labels:
    app: code-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: code-agent
  template:
    metadata:
      labels:
        app: code-agent
    spec:
      containers:
      - name: api
        image: code-agent:0.1.0
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: LLM_PROVIDER
          value: "anthropic"
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: code-agent-secrets
              key: anthropic-api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: code-agent-service
  namespace: default
spec:
  type: LoadBalancer
  selector:
    app: code-agent
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

### Secret

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: code-agent-secrets
  namespace: default
type: Opaque
data:
  # Base64 encoded API keys
  anthropic-api-key: <base64-encoded-key>
  openai-api-key: <base64-encoded-key>
```

```bash
# Criar secret
kubectl create secret generic code-agent-secrets \
  --from-literal=anthropic-api-key=$ANTHROPIC_API_KEY \
  --from-literal=openai-api-key=$OPENAI_API_KEY
```

### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: code-agent-config
  namespace: default
data:
  LLM_PROVIDER: "anthropic"
  LLM_MODEL: "claude-sonnet-4-20250514"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
```

### Deploy

```bash
# Apply manifests
kubectl apply -f k8s/

# Ver status
kubectl get pods -l app=code-agent
kubectl get svc code-agent-service

# Logs
kubectl logs -f deployment/code-agent

# Scale
kubectl scale deployment code-agent --replicas=5

# Update
kubectl set image deployment/code-agent api=code-agent:0.2.0
kubectl rollout status deployment/code-agent

# Rollback
kubectl rollout undo deployment/code-agent
```

---

## ☁️ Cloud Providers

### AWS

#### EC2

```bash
# Launch instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name my-key \
  --security-groups code-agent-sg \
  --user-data file://user-data.sh

# user-data.sh
#!/bin/bash
apt update
apt install -y python3-pip git
# ... resto do setup
```

#### ECS (Fargate)

```json
{
  "family": "code-agent",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [{
    "name": "api",
    "image": "your-ecr-repo/code-agent:latest",
    "portMappings": [{
      "containerPort": 8000,
      "protocol": "tcp"
    }],
    "environment": [
      {"name": "LLM_PROVIDER", "value": "anthropic"}
    ],
    "secrets": [
      {
        "name": "ANTHROPIC_API_KEY",
        "valueFrom": "arn:aws:secretsmanager:..."
      }
    ]
  }]
}
```

### Google Cloud Platform

#### Cloud Run

```bash
# Build e push
gcloud builds submit --tag gcr.io/PROJECT_ID/code-agent

# Deploy
gcloud run deploy code-agent \
  --image gcr.io/PROJECT_ID/code-agent \
  --platform managed \
  --region us-central1 \
  --set-env-vars LLM_PROVIDER=anthropic \
  --set-secrets ANTHROPIC_API_KEY=anthropic-key:latest \
  --allow-unauthenticated
```

### Azure

#### Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name code-agent \
  --image myregistry.azurecr.io/code-agent:latest \
  --dns-name-label code-agent \
  --ports 8000 \
  --environment-variables \
    LLM_PROVIDER=anthropic \
  --secure-environment-variables \
    ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
```

---

## ✅ Produção Checklist

### Segurança

- [ ] HTTPS habilitado (SSL/TLS)
- [ ] API keys em secrets manager (não em .env)
- [ ] Firewall configurado (apenas portas necessárias)
- [ ] Rate limiting ativo
- [ ] Security headers configurados
- [ ] CORS restrito a origens conhecidas
- [ ] Logs de auditoria habilitados

### Performance

- [ ] Gunicorn/Uvicorn com múltiplos workers
- [ ] Connection pooling configurado
- [ ] Cache implementado (Redis)
- [ ] Database indexado
- [ ] Static files via CDN
- [ ] Gzip compression ativo

### Monitoring

- [ ] Health checks configurados
- [ ] Prometheus metrics expostas
- [ ] Grafana dashboards criados
- [ ] Alertas configurados (PagerDuty, Slack)
- [ ] APM implementado (DataDog, New Relic)
- [ ] Log aggregation (ELK, Splunk)

### Backup & Recovery

- [ ] Backup automático do DB
- [ ] Disaster recovery plan
- [ ] RTO/RPO definidos
- [ ] Testes de restore regulares

### Documentation

- [ ] API docs publicadas
- [ ] Runbooks criados
- [ ] Oncall procedures documentadas
- [ ] Architecture diagrams atualizados

---

## 📊 Monitoramento

### Prometheus Metrics

```python
# app/monitoring.py
from prometheus_client import Counter, Histogram, Gauge

# Métricas
tasks_created = Counter('tasks_created_total', 'Total tasks created')
tasks_completed = Counter('tasks_completed_total', 'Total tasks completed')
task_duration = Histogram('task_duration_seconds', 'Task execution time')
active_tasks = Gauge('active_tasks', 'Currently active tasks')

# Uso
tasks_created.inc()
with task_duration.time():
    # executa task
    pass
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Code Agent Metrics",
    "panels": [
      {
        "title": "Tasks per Minute",
        "targets": [
          {
            "expr": "rate(tasks_created_total[1m])"
          }
        ]
      },
      {
        "title": "Task Duration",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, task_duration_seconds)"
          }
        ]
      }
    ]
  }
}
```

---

**Para produção, sempre teste em staging primeiro!** 🚀