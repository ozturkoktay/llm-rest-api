"""Provider factory for creating LLM providers.

Following the Factory Pattern and Open/Closed Principle.
"""

from ..config.settings import settings
from ..interfaces.llm_provider import ILLMProvider
from ..services.ollama_provider import OllamaProvider


class LLMProviderFactory:
  """Factory class for creating LLM providers.

  Follows Open/Closed Principle - can add new providers without modification.
  """

  @staticmethod
  def create_provider(
    provider_type: str | None = None, model_name: str | None = None
  ) -> ILLMProvider:
    """Create an LLM provider instance.

    Args:
        provider_type: Type of provider (defaults to settings.model_type)
        model_name: Name of the model to use (defaults to settings.model_name)

    Returns:
        ILLMProvider: An instance of the requested provider

    Raises:
        ValueError: If the provider type is not supported
    """
    provider_type = provider_type or settings.model_type
    model_name = model_name or settings.model_name

    if provider_type == "ollama":
      return OllamaProvider(base_url=settings.ollama_base_url, model_name=model_name)
    raise ValueError(f"Unsupported model type: {provider_type}")

  @staticmethod
  def create_ollama_provider(model_name: str | None = None) -> OllamaProvider:
    """Convenience method to create an Ollama provider.

    Args:
        model_name: Name of the model to use

    Returns:
        OllamaProvider: An instance of OllamaProvider
    """
    return OllamaProvider(
      base_url=settings.ollama_base_url,
      model_name=model_name or settings.model_name,
    )
