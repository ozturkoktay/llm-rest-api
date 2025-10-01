"""LLM Service following the Dependency Inversion Principle.

Depends on abstractions (ILLMProvider) not concretions.
"""

from collections.abc import AsyncGenerator

from ..config.logging_config import get_logger
from ..interfaces.llm_provider import ILLMProvider
from ..models.schemas import GenerateRequest, GenerateResponse
from .provider_factory import LLMProviderFactory

logger = get_logger()


class LLMService:
  """Service layer for LLM operations."""

  def __init__(self, provider: ILLMProvider):
    """Initialize the service with a provider.

    Args:
        provider: Any implementation of ILLMProvider
    """
    self._provider = provider
    self._factory = LLMProviderFactory()
    logger.info(f"LLM Service initialized with provider: {type(provider).__name__}")

  async def generate_text(
    self, request: GenerateRequest, model_override: str | None = None
  ) -> GenerateResponse:
    """Generate text using the configured provider or a specific model.

    Args:
        request: The generation request
        model_override: Optional model name to use instead of default

    Returns:
        GenerateResponse with the generated text
    """
    provider = self._get_provider_for_request(request, model_override)
    logger.debug(f"Generating text with provider: {type(provider).__name__}")
    return await provider.generate(request)

  def _get_provider_for_request(
    self, request: GenerateRequest, model_override: str | None = None
  ) -> ILLMProvider:
    """
    Get the appropriate provider for the request.
    Follows Strategy Pattern - selects provider based on request.

    Args:
        request: The generation request
        model_override: Optional model name override

    Returns:
        ILLMProvider: The provider to use for this request
    """
    model_name = model_override or request.model
    if model_name and model_name != self._provider.get_model_info().get("model_name"):
      logger.info(f"Switching to model: {model_name}")
      return self._factory.create_provider("ollama", model_name)
    return self._provider

  async def generate_text_stream(
    self, request: GenerateRequest, model_override: str | None = None
  ) -> AsyncGenerator[str, None]:
    """Generate text with streaming using the configured provider or a specific model.

    Args:
        request: The generation request
        model_override: Optional model name to use instead of default

    Yields:
        Chunks of generated text
    """
    provider = self._get_provider_for_request(request, model_override)
    stream = await provider.generate_stream(request)
    async for chunk in stream:
      yield chunk

  async def check_health(self) -> bool:
    """Check if the LLM service is healthy.

    Returns:
        True if healthy, False otherwise
    """
    return await self._provider.health_check()

  def get_provider_info(self) -> dict:
    """Get information about the current provider.

    Returns:
        Dictionary with provider information
    """
    return self._provider.get_model_info()
