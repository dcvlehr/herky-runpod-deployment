#!/usr/bin/env python3
"""
RunPod Serverless Handler for vLLM
OpenAI-compatible API for LLM inference
"""

import runpod
import os
import subprocess
import time
import requests

# Environment variables
MODEL_NAME = os.environ.get("MODEL_NAME", "microsoft/Phi-3-mini-4k-instruct")
VLLM_PORT = 8000

# Start vLLM server in background
print(f"Starting vLLM server with model: {MODEL_NAME}")
vllm_process = subprocess.Popen([
    "python3", "-m", "vllm.entrypoints.openai.api_server",
    "--model", MODEL_NAME,
    "--host", "0.0.0.0",
    "--port", str(VLLM_PORT),
    "--dtype", "auto",
    "--max-model-len", "4096",
    "--gpu-memory-utilization", "0.9"
], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# Wait for vLLM to be ready
print("Waiting for vLLM server to start...")
max_retries = 60
for i in range(max_retries):
    try:
        response = requests.get(f"http://localhost:{VLLM_PORT}/v1/models", timeout=2)
        if response.status_code == 200:
            print(f"vLLM server ready (attempt {i+1})")
            break
    except:
        time.sleep(5)
else:
    print("ERROR: vLLM server failed to start")
    raise Exception("vLLM server startup timeout")


def handler(job):
    """
    RunPod handler - forwards requests to local vLLM OpenAI server
    """
    try:
        job_input = job.get("input", {})

        # Extract parameters
        messages = job_input.get("messages", [])
        if not messages:
            # Support simple prompt format
            prompt = job_input.get("prompt", "")
            if prompt:
                messages = [{"role": "user", "content": prompt}]
            else:
                return {"error": "No messages or prompt provided"}

        model = job_input.get("model", MODEL_NAME)
        max_tokens = job_input.get("max_tokens", 512)
        temperature = job_input.get("temperature", 0.7)
        stream = job_input.get("stream", False)

        # Call local vLLM OpenAI server
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }

        print(f"Sending request to vLLM: {len(messages)} messages")
        response = requests.post(
            f"http://localhost:{VLLM_PORT}/v1/chat/completions",
            json=payload,
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            print("Successfully generated response")
            return result
        else:
            error_msg = f"vLLM error: {response.status_code} - {response.text}"
            print(error_msg)
            return {"error": error_msg}

    except Exception as e:
        error_msg = f"Handler error: {str(e)}"
        print(error_msg)
        return {"error": error_msg}


# Start RunPod serverless worker
print("Starting RunPod serverless worker...")
runpod.serverless.start({"handler": handler})
