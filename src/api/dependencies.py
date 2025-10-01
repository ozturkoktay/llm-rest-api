"""Dependency injection for FastAPI.

Following the Dependency Inversion Principle.
"""

from functools import lru_cache

from ..config.settings import settings
from ..services.document_service import DocumentService
from ..services.llm_service import LLMService
from ..services.ollama_provider import OllamaProvider
from ..services.pdf_processor import PDFProcessor


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


@lru_cache
def get_pdf_processor() -> PDFProcessor:
  """Dependency injection for PDF processor.

  Returns a configured PDF processor instance.
  """
  return PDFProcessor()


def get_document_service() -> DocumentService:
  """Dependency injection for Document service.

  Returns a configured Document service instance.
  """
  llm_service = get_llm_service()
  pdf_processor = get_pdf_processor()
  return DocumentService(llm_service, pdf_processor)
