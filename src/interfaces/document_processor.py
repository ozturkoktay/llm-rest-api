"""Interface for document processors following the Interface Segregation Principle.

This allows different document processing implementations to be swapped easily.
"""

from abc import ABC, abstractmethod


class IDocumentProcessor(ABC):
  """Abstract interface for document processors."""

  @abstractmethod
  async def extract_text(self, file_content: bytes, filename: str) -> str:
    """Extract text from a document.

    Args:
        file_content: The raw bytes of the document
        filename: The name of the file (used to determine processing method)

    Returns:
        Extracted text content from the document

    Raises:
        ValueError: If the document format is not supported or processing fails
    """

  @abstractmethod
  def supports_format(self, filename: str) -> bool:
    """Check if the processor supports the given file format.

    Args:
        filename: The name of the file to check

    Returns:
        True if the format is supported, False otherwise
    """
