FROM ollama/ollama:latest

# Install Python and dependencies for RunPod handler
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --no-cache-dir runpod requests

# Copy handler script
COPY handler.py /handler.py
RUN chmod +x /handler.py

# Pre-pull models to avoid cold start delays
# This runs ollama serve in background, pulls model, then stops
RUN ollama serve & \
    sleep 10 && \
    ollama pull phi3:mini && \
    pkill ollama

# Set working directory
WORKDIR /

# Expose Ollama port (for debugging)
EXPOSE 11434

# Start the handler (which starts ollama internally)
CMD ["python3", "/handler.py"]
