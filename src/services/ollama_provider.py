"""Ollama LLM Provider implementation.

Following Open/Closed Principle - can extend without modifying the interface.
"""

from collections.abc import AsyncGenerator
import time
from typing import Any

from fastapi import status
import httpx

from ..config.logging_config import get_logger
from ..config.settings import settings
from ..exceptions import ModelNotFoundError
from ..interfaces.llm_provider import ILLMProvider
from ..models.schemas import GenerateRequest, GenerateResponse

logger = get_logger()


class OllamaProvider(ILLMProvider):
  """Ollama implementation of the LLM provider."""

  def __init__(self, base_url: str | None = None, model_name: str | None = None):
    """Initialize the Ollama provider.

    Args:
        base_url: Base URL for Ollama API (defaults to settings)
        model_name: Name of the model to use (defaults to settings)
    """
    self.base_url = base_url or settings.ollama_base_url
    self.model_name = model_name or settings.model_name
    self.client = httpx.AsyncClient(timeout=settings.request_timeout)
    logger.info(
      f"OllamaProvider initialized: model={self.model_name}, url={self.base_url}"
    )

  async def generate(self, request: GenerateRequest) -> GenerateResponse:
    """Generate a response using Ollama."""
    logger.debug(f"Checking if model exists: {self.model_name}")
    model_exists = await self.check_model_exists(self.model_name)
    if not model_exists:
      logger.error(f"Model not found: {self.model_name}")
      raise ModelNotFoundError(self.model_name, "ollama")

    logger.info(f"Generating text with model: {self.model_name}")
    start_time = time.time()

    payload: dict[str, Any] = {
      "model": self.model_name,
      "prompt": request.prompt,
      "stream": False,
      "options": {
        "num_predict": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "top_k": request.top_k,
      },
    }

    if request.stop_sequences:
      payload["options"]["stop"] = request.stop_sequences

    try:
      response = await self.client.post(f"{self.base_url}/api/generate", json=payload)
      response.raise_for_status()
      data = response.json()

      generation_time = (time.time() - start_time) * 1000

      logger.success(
        f"Generated {data.get('eval_count', 0)} tokens in {generation_time:.2f}ms"
      )

      return GenerateResponse(
        generated_text=data.get("response", ""),
        prompt=request.prompt,
        model_used=self.model_name,
        tokens_generated=data.get("eval_count", 0),
        finish_reason=data.get("done_reason", "complete"),
        generation_time_ms=generation_time,
      )
    except httpx.HTTPError as e:
      logger.error(f"HTTP error during generation: {e}")
      raise Exception(f"Failed to generate response: {str(e)}") from e

  async def generate_stream(  # type: ignore[override]
    self, request: GenerateRequest
  ) -> AsyncGenerator[str, None]:
    """Generate a streaming response using Ollama."""
    logger.debug(f"Starting streaming generation with model: {self.model_name}")
    model_exists = await self.check_model_exists(self.model_name)
    if not model_exists:
      logger.error(f"Model not found for streaming: {self.model_name}")
      raise ModelNotFoundError(self.model_name, "ollama")

    payload: dict[str, Any] = {
      "model": self.model_name,
      "prompt": request.prompt,
      "stream": True,
      "options": {
        "num_predict": request.max_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "top_k": request.top_k,
      },
    }

    if request.stop_sequences:
      payload["options"]["stop"] = request.stop_sequences

    try:
      async with self.client.stream(
        "POST", f"{self.base_url}/api/generate", json=payload
      ) as response:
        response.raise_for_status()
        async for line in response.aiter_lines():
          if line:
            import json

            data = json.loads(line)
            if "response" in data:
              yield data["response"]
    except httpx.HTTPError as e:
      raise Exception(f"Failed to generate streaming response: {str(e)}") from e

  async def health_check(self) -> bool:
    """Check if Ollama is healthy."""
    try:
      response = await self.client.get(f"{self.base_url}/api/tags")
      return response.status_code == status.HTTP_200_OK
    except Exception:
      return False

  async def check_model_exists(self, model_name: str) -> bool:
    """Check if a model exists in Ollama.

    Args:
        model_name: Name of the model to check

    Returns:
        True if the model exists, False otherwise
    """
    try:
      response = await self.client.get(f"{self.base_url}/api/tags")
      if response.status_code != status.HTTP_200_OK:
        return False

      data = response.json()
      models = data.get("models", [])

      model_name_normalized = model_name.lower()
      if ":" not in model_name_normalized:
        model_name_normalized = f"{model_name_normalized}:latest"

      for model in models:
        model_full_name = model.get("name", "").lower()
        model_base_name = model.get("model", "").lower()

        if (
          model_name_normalized in (model_full_name, model_base_name)
          or model_full_name.startswith(f"{model_name.lower()}:")
          or model_base_name.startswith(f"{model_name.lower()}:")
        ):
          return True

      return False
    except Exception:
      return False

  def get_model_info(self) -> dict:
    """Get information about the Ollama model."""
    return {
      "provider": "ollama",
      "model_name": self.model_name,
      "base_url": self.base_url,
    }

  async def close(self):
    """Close the HTTP client."""
    await self.client.aclose()
