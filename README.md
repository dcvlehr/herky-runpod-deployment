# Herky Chat Bot - RunPod Serverless Deployment

Docker image for running Ollama (phi3:mini) on RunPod Serverless GPU.

## What This Does

- Runs Ollama with phi3:mini model on GPU
- Provides RunPod Serverless handler for API access
- Pre-pulls model to minimize cold start time
- Compatible with AnythingLLM Ollama API

## Build & Deploy

### 1. Build Docker Image

```bash
docker build -t dcvlehr/herky-ollama-runpod:latest .
```

### 2. Push to Docker Hub

```bash
docker login
docker push dcvlehr/herky-ollama-runpod:latest
```

### 3. Deploy to RunPod

1. Go to RunPod Console → Serverless
2. Click "New Endpoint"
3. Choose "Import from Docker Registry"
4. Enter: `dcvlehr/herky-ollama-runpod:latest`
5. Configure:
   - GPU: RTX A4000
   - Min Workers: 0
   - Max Workers: 1
   - Idle Timeout: 300 seconds

## Usage

### API Format

**Simple Prompt:**
```json
{
  "input": {
    "prompt": "What is 5+5?",
    "model": "phi3:mini"
  }
}
```

**Chat Messages:**
```json
{
  "input": {
    "messages": [
      {"role": "user", "content": "What is 5+5?"}
    ],
    "model": "phi3:mini"
  }
}
```

### Test Endpoint

```bash
curl -X POST https://api.runpod.ai/v2/{endpoint-id}/runsync \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "What is 5+5?", "model": "phi3:mini"}}'
```

## Files

- `handler.py` - RunPod serverless handler
- `Dockerfile` - Container definition with pre-pulled models
- `requirements.txt` - Python dependencies

## Performance

- Cold start: ~5-8 seconds (container + model load)
- Warm inference: ~2-5 seconds
- Model: phi3:mini (2.2 GB)

## Cost Optimization

- Scales to zero when idle ($0 cost)
- RTX A4000: ~$0.30/hr active time
- Expected: $2-6/month for typical usage
