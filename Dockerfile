FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    ca-certificates \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama manually (latest version for better GPU support)
RUN wget -O /usr/local/bin/ollama https://github.com/ollama/ollama/releases/download/v0.5.4/ollama-linux-amd64 && \
    chmod +x /usr/local/bin/ollama

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

# Set CUDA environment variables for Ollama GPU support
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV LD_LIBRARY_PATH=/usr/local/nvidia/lib:/usr/local/nvidia/lib64

# Expose Ollama port (for debugging)
EXPOSE 11434

# Start the handler (which starts ollama internally)
CMD ["python3", "/handler.py"]
