"""PDF document processor implementation.

Following Open/Closed Principle - can extend without modifying the interface.
"""

import io

from ..config.logging_config import get_logger
from ..interfaces.document_processor import IDocumentProcessor

logger = get_logger()


class PDFProcessor(IDocumentProcessor):
  """PDF implementation of the document processor."""

  def __init__(self):
    """Initialize the PDF processor."""
    try:
      import importlib.util

      self._pypdf_available = importlib.util.find_spec("pypdf") is not None
      logger.info("PDFProcessor initialized with pypdf")
    except (ImportError, ValueError):
      self._pypdf_available = False
      logger.warning(
        "pypdf not available. PDF processing will not work. "
        "Install with: pip install pypdf"
      )

  async def extract_text(self, file_content: bytes, filename: str) -> str:
    """Extract text from a PDF document.

    Args:
        file_content: The raw bytes of the PDF
        filename: The name of the PDF file

    Returns:
        Extracted text content from the PDF

    Raises:
        ValueError: If pypdf is not installed or processing fails
    """
    if not self._pypdf_available:
      logger.error("Attempted to process PDF without pypdf installed")
      raise ValueError(
        "PDF processing not available. Please install pypdf: pip install pypdf"
      )

    if not self.supports_format(filename):
      logger.error(f"Unsupported file format: {filename}")
      raise ValueError(f"Unsupported file format. Expected PDF, got: {filename}")

    try:
      import pypdf

      logger.info(f"Extracting text from PDF: {filename}")
      pdf_file = io.BytesIO(file_content)
      pdf_reader = pypdf.PdfReader(pdf_file)

      text_parts = []
      page_count = len(pdf_reader.pages)
      logger.debug(f"PDF has {page_count} pages")

      for page_num, page in enumerate(pdf_reader.pages, start=1):
        page_text = page.extract_text()
        if page_text.strip():
          text_parts.append(f"--- Page {page_num} ---\n{page_text}")
          logger.debug(f"Extracted {len(page_text)} characters from page {page_num}")

      full_text = "\n\n".join(text_parts)
      logger.success(
        f"Successfully extracted {len(full_text)} characters from {page_count} pages"
      )
      return full_text

    except Exception as e:
      logger.error(f"Failed to extract text from PDF: {e}")
      raise ValueError(f"Failed to process PDF: {str(e)}") from e

  def supports_format(self, filename: str) -> bool:
    """Check if the file is a PDF.

    Args:
        filename: The name of the file to check

    Returns:
        True if the file has a .pdf extension, False otherwise
    """
    return filename.lower().endswith(".pdf")
