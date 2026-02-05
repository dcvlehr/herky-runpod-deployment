# Use RunPod's official vLLM worker base image
FROM runpod/worker-vllm:stable-cuda12.1.0

# No additional setup needed - base image has everything
# Model will be specified via MODEL_NAME environment variable
