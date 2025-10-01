"""Custom exceptions for the AcSYS LLMs REST API."""


class ModelNotFoundError(Exception):
  """Exception raised when a requested model is not found.

  Provides helpful information about how to download the model.
  """

  def __init__(self, model_name: str, provider: str = "ollama"):
    """Initialize the exception.

    Args:
        model_name: Name of the model that was not found
        provider: Provider type (default: ollama)
    """
    self.model_name = model_name
    self.provider = provider
    self.message = self._generate_message()
    super().__init__(self.message)

  def _generate_message(self) -> str:
    """Generate a helpful error message with download instructions.

    Returns:
        Formatted error message with instructions
    """
    if self.provider == "ollama":
      return (
        f"Model '{self.model_name}' not found. "
        f"To download this model, run:\n\n"
        f"  ollama pull {self.model_name}\n\n"
        f"To see available models, run:\n"
        f"  ollama list\n\n"
        f"For more models, visit: https://ollama.ai/library"
      )
    return f"Model '{self.model_name}' not found for provider '{self.provider}'"

  def to_dict(self) -> dict:
    """Convert exception to dictionary for API response.

    Returns:
        Dictionary with error details and instructions
    """
    return {
      "error": "Model Not Found",
      "model_name": self.model_name,
      "provider": self.provider,
      "message": self.message,
      "instructions": self._get_instructions(),
    }

  def _get_instructions(self) -> dict:
    """Get structured installation instructions.

    Returns:
        Dictionary with installation commands and links
    """
    if self.provider == "ollama":
      return {
        "download_command": f"ollama pull {self.model_name}",
        "list_models_command": "ollama list",
        "browse_models_url": "https://ollama.ai/library",
      }
    return {}


class ProviderNotFoundError(Exception):
  """Exception raised when a provider type is not supported."""

  def __init__(self, provider_type: str):
    """Initialize the exception.

    Args:
        provider_type: The unsupported provider type
    """
    self.provider_type = provider_type
    self.message = f"Provider type '{provider_type}' is not supported"
    super().__init__(self.message)
