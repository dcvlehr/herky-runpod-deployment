FROM nvidia/cuda:12.1.0-base-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install Python dependencies
RUN pip3 install --no-cache-dir runpod==1.6.2 requests==2.31.0

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
