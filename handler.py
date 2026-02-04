#!/usr/bin/env python3
"""
RunPod Serverless Handler for Ollama
Provides Ollama-compatible API for phi3:mini inference on GPU
"""

import runpod
import subprocess
import requests
import time
import os
import json

# Start Ollama in background on first import
print("Starting Ollama service...")
ollama_process = subprocess.Popen(
    ["/usr/local/bin/ollama", "serve"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
time.sleep(5)  # Wait for Ollama to start
print("Ollama service started")

# Track if models are pulled
models_pulled = False


def pull_models():
    """Pull required models on first run"""
    global models_pulled
    if not models_pulled:
        print("Pulling phi3:mini model...")
        result = subprocess.run(
            ["ollama", "pull", "phi3:mini"],
            capture_output=True,
            text=True
        )
        print(f"phi3:mini pull result: {result.returncode}")
        if result.returncode != 0:
            print(f"Error: {result.stderr}")

        models_pulled = True
        print("Models ready")


def handler(job):
    """
    RunPod serverless handler
    Accepts Ollama-compatible API requests and forwards to local Ollama
    """
    try:
        # Ensure models are pulled
        pull_models()

        job_input = job.get("input", {})

        # Support both direct prompt and Ollama API format
        if "prompt" in job_input:
            # Simple format: {"prompt": "text", "model": "phi3:mini"}
            prompt = job_input.get("prompt", "")
            model = job_input.get("model", "phi3:mini")
            stream = job_input.get("stream", False)

            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream
            }
            endpoint = "http://localhost:11434/api/generate"

        elif "messages" in job_input:
            # Chat format: {"messages": [...], "model": "phi3:mini"}
            messages = job_input.get("messages", [])
            model = job_input.get("model", "phi3:mini")
            stream = job_input.get("stream", False)

            payload = {
                "model": model,
                "messages": messages,
                "stream": stream
            }
            endpoint = "http://localhost:11434/api/chat"

        else:
            return {
                "error": "Invalid input format. Expected 'prompt' or 'messages' field."
            }

        # Call Ollama API
        print(f"Calling Ollama API: {endpoint}")
        response = requests.post(
            endpoint,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(f"Success: Generated response")
            return result
        else:
            error_msg = f"Ollama API error: {response.status_code} - {response.text}"
            print(error_msg)
            return {"error": error_msg}

    except Exception as e:
        error_msg = f"Handler error: {str(e)}"
        print(error_msg)
        return {"error": error_msg}


# Start the RunPod serverless handler
print("Starting RunPod handler...")
runpod.serverless.start({"handler": handler})
