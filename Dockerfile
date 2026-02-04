# Use official Ollama image with CUDA support (has working Ollama + CUDA libs)
FROM ollama/ollama:latest

# Install Python for RunPod handler
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --no-cache-dir runpod==1.6.2 requests==2.31.0

# Copy handler script
COPY handler.py /handler.py
RUN chmod +x /handler.py

# Pre-pull models to avoid cold start delays
RUN /bin/ollama serve & \
    sleep 10 && \
    /bin/ollama pull phi3:mini && \
    pkill ollama

# Set working directory
WORKDIR /

# Expose Ollama port
EXPOSE 11434

# Start the handler (which starts ollama internally)
CMD ["python3", "/handler.py"]
