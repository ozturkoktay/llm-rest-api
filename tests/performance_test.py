"""Performance and load testing for the LLM API.

Tests concurrent requests and measures response times.
"""

import asyncio
import time

from fastapi import status
import httpx


async def send_request(
  client: httpx.AsyncClient, request_id: int
) -> tuple[int, float, bool]:
  """Send a single request and measure response time.

  Returns:
      (request_id, response_time_ms, success)
  """
  url = "http://localhost:8000/api/v1/generate"
  payload = {
    "prompt": f"Generate a short response for request {request_id}",
    "max_tokens": 50,
    "temperature": 0.7,
  }

  start_time = time.time()
  try:
    response = await client.post(url, json=payload, timeout=60.0)
    elapsed_ms = (time.time() - start_time) * 1000
    success = response.status_code == status.HTTP_200_OK
    return (request_id, elapsed_ms, success)
  except Exception as e:
    elapsed_ms = (time.time() - start_time) * 1000
    print(f"Request {request_id} failed: {e}")
    return (request_id, elapsed_ms, False)


async def run_concurrent_test(num_requests: int, concurrent: int):
  """Run concurrent requests to test API performance.

  Args:
      num_requests: Total number of requests to send
      concurrent: Number of concurrent requests
  """
  print(f"\n{'=' * 60}")
  print(f"Load Test: {num_requests} requests with {concurrent} concurrent")
  print(f"{'=' * 60}\n")

  async with httpx.AsyncClient() as client:
    results = []
    for i in range(0, num_requests, concurrent):
      batch_size = min(concurrent, num_requests - i)
      tasks = [send_request(client, i + j) for j in range(batch_size)]
      batch_results = await asyncio.gather(*tasks)
      results.extend(batch_results)

      completed = i + batch_size
      print(f"Progress: {completed}/{num_requests} requests completed")

  successful = [r for r in results if r[2]]
  failed = [r for r in results if not r[2]]

  if successful:
    response_times = [r[1] for r in successful]
    avg_time = sum(response_times) / len(response_times)
    min_time = min(response_times)
    max_time = max(response_times)

    sorted_times = sorted(response_times)
    p50 = sorted_times[len(sorted_times) // 2]
    p95 = sorted_times[int(len(sorted_times) * 0.95)]
    p99 = sorted_times[int(len(sorted_times) * 0.99)]

    print(f"\n{'=' * 60}")
    print("Results:")
    print(f"{'=' * 60}")
    print(f"Total Requests:     {len(results)}")
    print(
      f"Successful:         {len(successful)} ({len(successful) / len(results) * 100:.1f}%)"
    )
    print(
      f"Failed:             {len(failed)} ({len(failed) / len(results) * 100:.1f}%)"
    )
    print("\nResponse Times (ms):")
    print(f"  Average:          {avg_time:.2f}")
    print(f"  Min:              {min_time:.2f}")
    print(f"  Max:              {max_time:.2f}")
    print(f"  Median (P50):     {p50:.2f}")
    print(f"  P95:              {p95:.2f}")
    print(f"  P99:              {p99:.2f}")
    print(f"{'=' * 60}\n")
  else:
    print("\nAll requests failed!")


async def test_health():
  """Test the health endpoint."""
  print("Testing health endpoint...")
  async with httpx.AsyncClient() as client:
    try:
      response = await client.get("http://localhost:8000/api/v1/health")
      if response.status_code == status.HTTP_200_OK:
        print("Health check passed")
        print(f"   Response: {response.json()}\n")
        return True
      print(f"Health check failed: {response.status_code}\n")
      return False
    except Exception as e:
      print(f"Could not connect to API: {e}\n")
      return False


async def main():
  """Run performance tests."""
  print("\nLLM API Performance Test")
  print("=" * 60)

  if not await test_health():
    print("Please ensure the API is running (python main.py)")
    return

  tests = [
    (5, 1),
    (10, 2),
    (10, 5),
  ]

  for num_requests, concurrent in tests:
    await run_concurrent_test(num_requests, concurrent)
    await asyncio.sleep(2)

  print("\nPerformance testing complete!")


if __name__ == "__main__":
  try:
    asyncio.run(main())
  except KeyboardInterrupt:
    print("\n\nTest interrupted by user.")
