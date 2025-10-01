"""Simple test to verify the model checking feature works correctly.

Run this after starting the API server.
"""

import json
import subprocess
import sys


def test_with_curl():
  """Test the API using curl commands."""
  print("=" * 70)
  print("Testing Model Not Found Feature with curl")
  print("=" * 70)

  print("\n1. Testing with non-existent model 'llama3'...")
  print("-" * 70)

  result = subprocess.run(  # noqa: S603
    [  # noqa: S607
      "curl",
      "-s",
      "-X",
      "POST",
      "http://localhost:8001/llm-api/v1/generate",
      "-H",
      "Content-Type: application/json",
      "-d",
      json.dumps({"prompt": "Hello!", "model": "llama3"}),
    ],
    check=False,
    capture_output=True,
    text=True,
  )

  if result.returncode == 0:
    try:
      response = json.loads(result.stdout)
      if "detail" in response:
        detail = response["detail"]
        print("✓ Got expected error response (404)")
        print(f"\nError: {detail.get('error')}")
        print(f"Model: {detail.get('model_name')}")
        print(f"Provider: {detail.get('provider')}")
        print("\nInstructions:")
        instructions = detail.get("instructions", {})
        print(f"  Download: {instructions.get('download_command')}")
        print(f"  List: {instructions.get('list_models_command')}")
        print(f"  Browse: {instructions.get('browse_models_url')}")
      else:
        print(f"Unexpected response: {response}")
    except json.JSONDecodeError:
      print(f"Failed to parse JSON: {result.stdout}")
  else:
    print(f"curl command failed: {result.stderr}")

  print("\n" + "=" * 70)
  print("\n2. Testing with existing model 'deepseek-r1'...")
  print("-" * 70)

  result = subprocess.run(  # noqa: S603
    [  # noqa: S607
      "curl",
      "-s",
      "-X",
      "POST",
      "http://localhost:8001/llm-api/v1/generate",
      "-H",
      "Content-Type: application/json",
      "-d",
      json.dumps(
        {"prompt": "Say hello in one word", "model": "deepseek-r1", "max_tokens": 10}
      ),
    ],
    check=True,
    capture_output=True,
    text=True,
    timeout=30,
  )

  if result.returncode == 0:
    try:
      response = json.loads(result.stdout)
      if "generated_text" in response:
        print("✓ Generation successful!")
        print(f"Model used: {response.get('model_used')}")
        print(f"Tokens: {response.get('tokens_generated')}")
        print(f"Response: {response.get('generated_text')[:100]}...")
      elif "detail" in response:
        print(f"✗ Got error: {response['detail']}")
      else:
        print(f"Unexpected response: {response}")
    except json.JSONDecodeError:
      print(f"Failed to parse JSON: {result.stdout}")
  else:
    print(f"curl command failed: {result.stderr}")

  print("\n" + "=" * 70)
  print("Test Complete!")
  print("=" * 70)


if __name__ == "__main__":
  try:
    test_with_curl()
  except KeyboardInterrupt:
    print("\n\nTest interrupted by user")
    sys.exit(1)
  except Exception as e:
    print(f"\n\nTest failed with error: {e}")
    sys.exit(1)
