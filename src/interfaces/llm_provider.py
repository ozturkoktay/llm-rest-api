"""Interface for LLM providers following the Interface Segregation Principle.

This allows different LLM implementations to be swapped easily.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from ..models.schemas import GenerateRequest, GenerateResponse


class ILLMProvider(ABC):
  """Abstract interface for LLM providers."""

  @abstractmethod
  async def generate(self, request: GenerateRequest) -> GenerateResponse:
    """Generate a response from the LLM model.

    Args:
        request: The generation request containing prompt and parameters

    Returns:
        GenerateResponse containing the generated text and metadata
    """

  @abstractmethod
  async def generate_stream(
    self, request: GenerateRequest
  ) -> AsyncGenerator[str, None]:
    """Generate a streaming response from the LLM model.

    Args:
        request: The generation request containing prompt and parameters

    Yields:
        Chunks of generated text
    """

  @abstractmethod
  async def health_check(self) -> bool:
    """Check if the LLM provider is healthy and ready to serve requests.

    Returns:
        True if healthy, False otherwise
    """

  @abstractmethod
  async def check_model_exists(self, model_name: str) -> bool:
    """Check if a specific model exists in the provider.

    Args:
        model_name: Name of the model to check

    Returns:
        True if the model exists, False otherwise
    """

  @abstractmethod
  def get_model_info(self) -> dict:
    """Get information about the loaded model.

    Returns:
        Dictionary containing model information
    """
