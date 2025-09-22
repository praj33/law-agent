# Law Agent Deployment Guide

This guide provides comprehensive instructions for deploying the Law Agent system in various environments.

## Quick Start

### 1. Prerequisites

- Python 3.9 or higher
- Redis server (for caching and session storage)
- SQLite (included) or PostgreSQL (for production)
- 4GB+ RAM recommended
- 2GB+ disk space

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd law_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration
```

### 3. Basic Setup

```bash
# Create required directories
mkdir -p logs models data

# Initialize database (if using PostgreSQL)
# python -c "from law_agent.database.init_db import init_database; init_database()"

# Start Redis server (if not running)
redis-server

# Run the system
python run_law_agent.py
```

The system will be available at:
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

## Production Deployment

### Docker Deployment

1. **Create Dockerfile**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p logs models data

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "run_law_agent.py"]
```

2. **Create docker-compose.yml**:

```yaml
version: '3.8'

services:
  law-agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/lawagent
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
      - ./models:/app/models
      - ./data:/app/data

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=lawagent
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

3. **Deploy**:

```bash
docker-compose up -d
```

### Kubernetes Deployment

1. **Create ConfigMap**:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: law-agent-config
data:
  DATABASE_URL: "postgresql://user:password@postgres:5432/lawagent"
  REDIS_URL: "redis://redis:6379/0"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  LOG_LEVEL: "INFO"
```

2. **Create Deployment**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: law-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: law-agent
  template:
    metadata:
      labels:
        app: law-agent
    spec:
      containers:
      - name: law-agent
        image: law-agent:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: law-agent-config
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
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

3. **Create Service**:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: law-agent-service
spec:
  selector:
    app: law-agent
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Environment Configuration

### Required Environment Variables

```bash
# Database Configuration
DATABASE_URL=sqlite:///./law_agent.db  # or PostgreSQL URL
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false  # Set to false in production

# Security
SECRET_KEY=your-secure-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI/ML Configuration (optional)
HUGGINGFACE_TOKEN=your-huggingface-token
OPENAI_API_KEY=your-openai-key

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/law_agent.log

# Reinforcement Learning
RL_MODEL_PATH=models/rl_policy
RL_LEARNING_RATE=0.001
RL_EXPLORATION_RATE=0.1

# Vector Database
CHROMA_PERSIST_DIRECTORY=./chroma_db
VECTOR_DIMENSION=384

# Monitoring
PROMETHEUS_PORT=9090
ENABLE_METRICS=true
```

### Production Security Settings

```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Use strong database passwords
# Enable SSL/TLS for database connections
# Configure firewall rules
# Set up reverse proxy (nginx/Apache)
# Enable HTTPS with SSL certificates
```

## Performance Optimization

### 1. Database Optimization

```sql
-- PostgreSQL indexes for better performance
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_interactions_user_id ON interactions(user_id);
CREATE INDEX idx_interactions_timestamp ON interactions(timestamp);
CREATE INDEX idx_interactions_domain ON interactions(predicted_domain);
```

### 2. Redis Configuration

```bash
# redis.conf optimizations
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 3. Application Tuning

```python
# In production, consider:
# - Increasing worker processes
# - Using connection pooling
# - Implementing request queuing
# - Adding load balancing
```

## Monitoring and Logging

### 1. Prometheus Metrics

The system exposes metrics at `/metrics`:

- `law_agent_requests_total` - Total requests
- `law_agent_request_duration_seconds` - Request duration
- `law_agent_queries_total` - Legal queries processed
- `law_agent_feedback_total` - User feedback received

### 2. Log Aggregation

Configure log aggregation with ELK stack or similar:

```yaml
# docker-compose.yml addition
  elasticsearch:
    image: elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: logstash:8.5.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch

  kibana:
    image: kibana:8.5.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

### 3. Health Checks

The system provides health check endpoints:

- `/health` - Basic health check
- `/api/v1/system/health` - Detailed system health
- `/api/v1/system/info` - System information

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer Configuration**:

```nginx
upstream law_agent {
    server law-agent-1:8000;
    server law-agent-2:8000;
    server law-agent-3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://law_agent;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

2. **Session Affinity**: Use Redis for session storage to enable stateless scaling.

3. **Database Scaling**: Consider read replicas for PostgreSQL.

### Vertical Scaling

- **Memory**: 4GB minimum, 8GB+ recommended for production
- **CPU**: 2+ cores recommended
- **Storage**: SSD recommended for database and model storage

## Backup and Recovery

### 1. Database Backup

```bash
# PostgreSQL backup
pg_dump -h localhost -U user lawagent > backup_$(date +%Y%m%d).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U user lawagent | gzip > $BACKUP_DIR/lawagent_$DATE.sql.gz
find $BACKUP_DIR -name "lawagent_*.sql.gz" -mtime +7 -delete
```

### 2. Model and Data Backup

```bash
# Backup RL models and vector database
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/ chroma_db/
```

### 3. Recovery Procedures

```bash
# Database recovery
gunzip -c backup_20240129.sql.gz | psql -h localhost -U user lawagent

# Model recovery
tar -xzf models_backup_20240129.tar.gz
```

## Troubleshooting

### Common Issues

1. **Memory Issues**:
   - Increase container memory limits
   - Optimize model loading
   - Implement model caching

2. **Database Connection Issues**:
   - Check connection strings
   - Verify database server status
   - Check firewall rules

3. **Redis Connection Issues**:
   - Verify Redis server status
   - Check Redis configuration
   - Monitor Redis memory usage

4. **Performance Issues**:
   - Enable caching
   - Optimize database queries
   - Monitor system resources

### Debug Mode

```bash
# Run in debug mode
python run_law_agent.py --dev

# Check logs
tail -f logs/law_agent.log

# Monitor metrics
curl http://localhost:8000/metrics
```

## Security Considerations

1. **API Security**:
   - Implement rate limiting
   - Use HTTPS in production
   - Validate all inputs
   - Implement proper authentication

2. **Database Security**:
   - Use strong passwords
   - Enable SSL connections
   - Regular security updates
   - Backup encryption

3. **Infrastructure Security**:
   - Network segmentation
   - Firewall configuration
   - Regular security audits
   - Container security scanning

## Support and Maintenance

### Regular Maintenance Tasks

1. **Daily**:
   - Monitor system health
   - Check error logs
   - Verify backup completion

2. **Weekly**:
   - Review performance metrics
   - Update RL models
   - Clean up old logs

3. **Monthly**:
   - Security updates
   - Database maintenance
   - Performance optimization review

### Getting Help

- Check logs: `logs/law_agent.log`
- System health: `http://localhost:8000/api/v1/system/health`
- Performance metrics: `http://localhost:8000/metrics`
- Run tests: `python run_law_agent.py --test`
