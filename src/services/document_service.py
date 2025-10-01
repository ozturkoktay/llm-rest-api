"""Document service for handling document processing and question answering.

Follows Single Responsibility Principle - handles document + LLM interaction.
"""

from ..config.logging_config import get_logger
from ..interfaces.document_processor import IDocumentProcessor
from ..models.schemas import DocumentQuestionRequest, GenerateRequest
from ..services.llm_service import LLMService

logger = get_logger()


class DocumentService:
  """Service for processing documents and answering questions about them."""

  def __init__(self, llm_service: LLMService, document_processor: IDocumentProcessor):
    """Initialize the document service.

    Args:
        llm_service: Service for generating text with LLM
        document_processor: Processor for extracting text from documents
    """
    self._llm_service = llm_service
    self._document_processor = document_processor
    logger.info("DocumentService initialized")

  async def answer_question_about_document(
    self, request: DocumentQuestionRequest, file_content: bytes, filename: str
  ):
    """Answer a question about a document.

    Args:
        request: The question request with parameters
        file_content: The raw bytes of the document
        filename: The name of the document file

    Returns:
        GenerateResponse with the answer to the question

    Raises:
        ValueError: If document processing fails or format is unsupported
    """
    logger.info(f"Processing document question for file: {filename}")

    # Extract text from document
    if not self._document_processor.supports_format(filename):
      logger.error(f"Unsupported document format: {filename}")
      raise ValueError(
        "Unsupported document format. Only PDF files are currently supported."
      )

    document_text = await self._document_processor.extract_text(file_content, filename)
    logger.info(f"Extracted {len(document_text)} characters from document: {filename}")

    # Build prompt with document context
    prompt = self._build_prompt(request.question, document_text, request.context_mode)
    logger.debug(f"Built prompt with {len(prompt)} characters")

    # Create generation request
    generate_request = GenerateRequest(
      prompt=prompt,
      max_tokens=request.max_tokens,
      temperature=request.temperature,
      top_p=request.top_p,
      top_k=request.top_k,
      stop_sequences=request.stop_sequences,
      stream=False,
      model=request.model,
    )

    # Generate answer using LLM
    response = await self._llm_service.generate_text(generate_request)
    logger.success(f"Generated answer to document question about {filename}")

    return response

  def _build_prompt(
    self, question: str, document_text: str, context_mode: str = "full"
  ) -> str:
    """Build a prompt for the LLM with document context.

    Args:
        question: The user's question
        document_text: The extracted text from the document
        context_mode: How to include context ('full', 'summary', or 'smart')

    Returns:
        Formatted prompt string
    """
    if context_mode == "summary":
      # Truncate very long documents
      max_chars = 4000
      if len(document_text) > max_chars:
        document_text = document_text[:max_chars] + "\n\n[... document truncated ...]"
        logger.debug(f"Document text truncated to {max_chars} characters")

    return f"""Based on the following document content, please answer the question.

Document Content:
{document_text}

Question: {question}

Answer:"""
