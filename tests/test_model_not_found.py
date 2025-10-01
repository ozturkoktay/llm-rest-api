"""Test script to demonstrate the model not found feature."""

import asyncio

from fastapi import status
import httpx


async def test_model_not_found():
  """Test requesting a model that doesn't exist."""
  base_url = "http://localhost:8000"

  print("=" * 60)
  print("Testing Model Not Found Feature")
  print("=" * 60)

  async with httpx.AsyncClient() as client:
    print("\n1. Testing with existing model (deepseek-r1)...")
    try:
      response = await client.post(
        f"{base_url}/generate",
        json={
          "prompt": "Hello, how are you?",
          "model": "deepseek-r1",
        },
        timeout=30.0,
      )
      print(f"Status: {response.status_code}")
      if response.status_code == status.HTTP_200_OK:
        print("✓ Model found and working!")
        data = response.json()
        print(f"Model used: {data['model_used']}")
      else:
        print(f"Response: {response.json()}")
    except Exception as e:
      print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("\n2. Testing with non-existent model (llama3)...")
    try:
      response = await client.post(
        f"{base_url}/generate",
        json={
          "prompt": "Hello, how are you?",
          "model": "llama3",
        },
        timeout=30.0,
      )
      print(f"Status: {response.status_code}")
      print("\nResponse:")
      print("-" * 60)
      data = response.json()
      if response.status_code == status.HTTP_404_NOT_FOUND:
        print("✓ Model not found - helpful error returned!")
        print(f"\nError: {data['detail']['error']}")
        print(f"Model: {data['detail']['model_name']}")
        print(f"\nMessage:\n{data['detail']['message']}")
        print("\nInstructions:")
        for key, value in data["detail"]["instructions"].items():
          print(f"  {key}: {value}")
      else:
        print(data)
    except Exception as e:
      print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("\n3. Testing with another non-existent model (gpt-4)...")
    try:
      response = await client.post(
        f"{base_url}/generate",
        json={
          "prompt": "What is AI?",
          "model": "gpt-4",
        },
        timeout=30.0,
      )
      print(f"Status: {response.status_code}")
      if response.status_code == status.HTTP_404_NOT_FOUND:
        print("✓ Model not found - helpful error returned!")
        data = response.json()
        print("\nDownload command:")
        print(f"  {data['detail']['instructions']['download_command']}")
      else:
        print(f"Response: {response.json()}")
    except Exception as e:
      print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("\nTest Complete!")
    print("=" * 60)


if __name__ == "__main__":
  asyncio.run(test_model_not_found())
