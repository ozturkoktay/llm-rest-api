"""Dependency injection for FastAPI.

Following the Dependency Inversion Principle.
"""

from functools import lru_cache

from ..config.settings import settings
from ..services.llm_service import LLMService
from ..services.ollama_provider import OllamaProvider


@lru_cache
def get_llm_provider():
  """Factory function to get the appropriate LLM provider.

  This can be extended to support multiple providers based on configuration.
  """
  if settings.model_type == "ollama":
    return OllamaProvider(
      base_url=settings.ollama_base_url, model_name=settings.model_name
    )
  raise ValueError(f"Unsupported model type: {settings.model_type}")


def get_llm_service() -> LLMService:
  """Dependency injection for LLM service.

  Returns a configured LLM service instance.
  """
  provider = get_llm_provider()
  return LLMService(provider)
