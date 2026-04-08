# Deployment Guide

This guide covers various deployment options for the Cyber Incident Response OpenEnv.

## Local Development

### Prerequisites
- Python 3.8+
- pip or conda

### Setup

1. **Clone and navigate to the project**:
   ```bash
   git clone https://github.com/your-org/cyber-incident-openenv.git
   cd cyber-incident-openenv
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

5. **Start the server**:
   ```bash
   python -m uvicorn server:app --reload --port 7860
   ```

The API will be available at `http://localhost:7860`

View interactive docs at `http://localhost:7860/docs`

## Docker Deployment

### Build Image
```bash
docker build -t cyber-incident-openenv:latest .
```

### Run Container
```bash
docker run -p 7860:7860 \
  -e USE_LLM=false \
  -e LOG_LEVEL=INFO \
  cyber-incident-openenv:latest
```

### With Environment File
```bash
docker run -p 7860:7860 \
  --env-file .env \
  cyber-incident-openenv:latest
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  cyber-incident-env:
    build: .
    ports:
      - "7860:7860"
    environment:
      - USE_LLM=false
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7860/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
```

Run with:
```bash
docker-compose up -d
```

## Hugging Face Spaces Deployment

### Prerequisites
- Hugging Face account
- Hugging Face CLI installed: `pip install huggingface-hub`

### Steps

1. **Create a new Space** on Hugging Face (Docker runtime)

2. **Configure Secrets** (if using LLM):
   - Go to Space Settings → Secrets
   - Add `HF_TOKEN` with your API key

3. **Push to Spaces**:
   ```bash
   huggingface-cli login
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://huggingface.co/spaces/your-username/cyber-incident-openenv
   git push -u origin main
   ```

The Space will auto-build and deploy. Access your app at:
`https://huggingface.co/spaces/your-username/cyber-incident-openenv`

## Production Considerations

### Environment Variables
- Set `USE_LLM=false` unless you have validated API credentials
- Set `LOG_LEVEL=INFO` or `WARNING` for production
- Use strong API keys in `.env` (never commit to repo)

### Security
- Use HTTPS in production (reverse proxy with nginx/Apache)
- Implement rate limiting for API endpoints
- Validate all inputs (already handled via Pydantic)
- Set CORS appropriately for your client domain

### Monitoring
- Enable logging with `LOG_LEVEL=INFO`
- Monitor container health checks
- Set up alerts for failed API calls

### Scaling
- Use load balancer for multiple instances
- Each instance runs independently
- Stateless design allows horizontal scaling

## Testing Deployment

After deployment, test with:

```bash
# Health check
curl http://your-server:7860/

# Get available tasks
curl http://your-server:7860/tasks

# Reset environment
curl -X POST http://your-server:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "easy"}'

# Execute a step
curl -X POST http://your-server:7860/step \
  -H "Content-Type: application/json" \
  -d '{"action": {"investigate_host": "workstation_1"}}'
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 7860
lsof -i :7860  # Linux/Mac
netstat -ano | findstr :7860  # Windows

# Kill process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

### Certificate Issues with HTTPS
- Ensure SSL certificates are valid
- For self-signed certs in testing: `curl --insecure https://...`

### Memory Issues
- Increase Docker memory limit: `docker run -m 4g ...`
- Or via docker-compose: `mem_limit: 4g`

### API Quota Exceeded
- Keep `USE_LLM=false` to avoid calling paid APIs
- Ensure `.env` is properly configured if enabling LLM

## Performance Tips

1. **Use rule-based agents** (USE_LLM=false) for best performance
2. **Enable caching** for repeated requests
3. **Use connection pooling** for database connections
4. **Monitor metrics** for bottlenecks

## Support

For deployment issues:
1. Check logs: `docker logs <container_id>`
2. Review CONTRIBUTING.md for bug reports
3. Check existing GitHub issues
4. Open a new issue with environment details
