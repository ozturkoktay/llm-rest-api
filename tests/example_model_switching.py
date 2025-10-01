"""Example demonstrating model switching feature.

Tests multiple models with the same prompt.
"""

import json

from fastapi import status
import requests


def test_model_switching():
  """Test switching between different models."""
  url = "http://localhost:8001/llm-api/v1/generate"

  prompt = "What is artificial intelligence?"
  models = ["llama2", "llama3", "mistral", "codellama"]

  print("Model Switching Demo")
  print("=" * 60)
  print(f"\nPrompt: {prompt}\n")

  for model in models:
    print(f"\n--- Testing with model: {model} ---")

    payload = {"prompt": prompt, "max_tokens": 100, "temperature": 0.7, "model": model}

    try:
      response = requests.post(url, json=payload, timeout=60)

      if response.status_code == status.HTTP_200_OK:
        result = response.json()
        print(f"Model Used: {result['model_used']}")
        print(f"Tokens: {result['tokens_generated']}")
        print(f"Time: {result['generation_time_ms']:.2f}ms")
        print(f"Response: {result['generated_text'][:100]}...")
      else:
        print(f"Error {response.status_code}: {response.text}")
        print(f"Note: Model '{model}' may not be available")
    except requests.exceptions.Timeout:
      print(f"Timeout for model: {model}")
    except requests.exceptions.ConnectionError:
      print("Error: Could not connect to API")
      print("Make sure the server is running (python main.py)")
      break
    except Exception as e:
      print(f"Unexpected error: {e}")


def test_default_vs_custom_model():
  """Compare default model vs custom model selection."""
  url = "http://localhost:8001/llm-api/v1/generate"
  prompt = "Hello, how are you?"

  print("\n\nDefault vs Custom Model Comparison")
  print("=" * 60)

  print("\n1. Using default model (from config):")
  payload_default = {"prompt": prompt, "max_tokens": 50, "temperature": 0.7}

  try:
    response = requests.post(url, json=payload_default, timeout=30)
    if response.status_code == status.HTTP_200_OK:
      result = response.json()
      print(f"   Model: {result['model_used']}")
      print(f"   Response: {result['generated_text'][:80]}...")
  except Exception as e:
    print(f"   Error: {e}")

  print("\n2. Using custom model (llama3):")
  payload_custom = {
    "prompt": prompt,
    "max_tokens": 50,
    "temperature": 0.7,
    "model": "llama3",
  }

  try:
    response = requests.post(url, json=payload_custom, timeout=30)
    if response.status_code == status.HTTP_200_OK:
      result = response.json()
      print(f"   Model: {result['model_used']}")
      print(f"   Response: {result['generated_text'][:80]}...")
    else:
      print("   Note: llama3 may not be available on your system")
  except Exception as e:
    print(f"   Error: {e}")


def test_streaming_with_model():
  """Test streaming with model switching."""
  url = "http://localhost:8001/llm-api/v1/generate/stream"

  print("\n\nStreaming with Model Switching")
  print("=" * 60)

  payload = {
    "prompt": "Count from 1 to 5",
    "max_tokens": 50,
    "temperature": 0.5,
    "model": "llama2",
  }

  print(f"\nUsing model: {payload['model']}")
  print("Streaming response: ", end="", flush=True)

  try:
    with requests.post(url, json=payload, stream=True, timeout=60) as response:
      if response.status_code == status.HTTP_200_OK:
        for line in response.iter_lines():
          if line:
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
              data = decoded[6:]
              if data != "[DONE]":
                try:
                  chunk = json.loads(data)
                  if "text" in chunk:
                    print(chunk["text"], end="", flush=True)
                except json.JSONDecodeError:
                  pass
        print("\n")
      else:
        print(f"\nError: {response.status_code}")
  except Exception as e:
    print(f"\nError: {e}")


if __name__ == "__main__":
  print("\nLLM API Model Switching Examples")
  print("=" * 60)
  print("\nNote: Make sure you have the models installed in Ollama:")
  print("  ollama pull llama2")
  print("  ollama pull llama3")
  print("  ollama pull mistral")
  print("=" * 60)

  try:
    test_default_vs_custom_model()
    test_streaming_with_model()
    test_model_switching()

    print("\n\n" + "=" * 60)
    print("Model switching demo complete!")
    print("=" * 60)

  except KeyboardInterrupt:
    print("\n\nDemo interrupted by user.")
