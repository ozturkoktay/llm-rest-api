"""Example client for testing the AcSYS LLMs REST API."""

import json

from fastapi import status
import requests


def test_generate():
  """Test non-streaming generation."""
  url = "http://192.168.51.164:8001/llm-api/v1/generate"

  payload = {
    "prompt": 'Return the PO number, date, and the total price without a currency sign of this PO document in the following JSON format and do not give me any other text: { "PONumber": "#####", "Date": YY/MM/DD, "Price": #### }\nThis is the PO document converted to a string: \nHaytek Millwright Services, LLCPurchase OrderDATE:8/14/2025ORDER #:PO-3120VENDORSHIP TOBen BelknapAcSYS Engineering LLC1095 W Melody AveGilbert, AZ 85233USAJosh TaitHaytek Millwright Services LLC4274 E 30th PlaceYuma, AZ 85365USAjosh@haytek.org(928) 750-5126ItemDescriptionPart NumberQtyRateAmtRec’d300-A05B-2518-D006 - Switch - Enable/On/OffFanuc Teach Pendant "Enable/On/Off" SwitchA05B-2518-D0061$260.00$260.000TOTAL$260.00\n',
    "max_tokens": 100,
    "temperature": 0.7,
  }

  print("Testing non-streaming generation...")
  print(f"Request: {json.dumps(payload, indent=2)}\n")

  response = requests.post(url, json=payload, timeout=30)

  if response.status_code == status.HTTP_200_OK:
    result = response.json()
    print("Response:")
    print(json.dumps(result, indent=2))
  else:
    print(f"Error: {response.status_code}")
    print(response.text)


def test_generate_stream():
  """Test streaming generation."""
  url = "http://192.168.51.164:8001/llm-api/v1/generate/stream"

  payload = {
    "prompt": "Write a haiku about programming",
    "max_tokens": 100,
    "temperature": 0.8,
  }

  print("\n\nTesting streaming generation...")
  print(f"Request: {json.dumps(payload, indent=2)}\n")
  print("Streaming response:")

  with requests.post(url, json=payload, stream=True, timeout=30) as response:
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
                elif "error" in chunk:
                  print(f"\nError: {chunk['error']}")
              except json.JSONDecodeError:
                pass
      print("\n")
    else:
      print(f"Error: {response.status_code}")
      print(response.text)


def test_health():
  """Test health check."""
  url = "http://192.168.51.164:8001/llm-api/v1/health"

  print("\n\nTesting health check...")
  response = requests.get(url, timeout=30)

  if response.status_code == status.HTTP_200_OK:
    result = response.json()
    print(json.dumps(result, indent=2))
  else:
    print(f"Error: {response.status_code}")
    print(response.text)


def test_model_info():
  """Test model info."""
  url = "http://192.168.51.164:8001/llm-api/v1/model/info"

  print("\n\nTesting model info...")
  response = requests.get(url, timeout=30)

  if response.status_code == status.HTTP_200_OK:
    result = response.json()
    print(json.dumps(result, indent=2))
  else:
    print(f"Error: {response.status_code}")
    print(response.text)


if __name__ == "__main__":
  try:
    test_health()
    test_model_info()
    test_generate()
    test_generate_stream()
  except requests.exceptions.ConnectionError:
    print("Error: Could not connect to the API. Make sure the server is running.")
  except KeyboardInterrupt:
    print("\nTest interrupted by user.")
