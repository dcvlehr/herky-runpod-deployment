# Use vLLM base image with CUDA support
FROM vllm/vllm-openai:latest

# Install RunPod SDK
RUN pip install runpod

# Copy handler
COPY handler.py /handler.py

# Set working directory
WORKDIR /

# Expose port for debugging
EXPOSE 8000

# Start handler
CMD ["python3", "-u", "/handler.py"]
