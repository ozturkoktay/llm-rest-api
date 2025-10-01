"""API routes for the LLM service.

Following RESTful principles and clean architecture.
"""

from collections.abc import AsyncGenerator
import json

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from ..config.logging_config import get_logger
from ..exceptions import ModelNotFoundError
from ..models.schemas import (
  DocumentQuestionRequest,
  ErrorResponse,
  GenerateRequest,
  GenerateResponse,
  HealthResponse,
)
from ..services.document_service import DocumentService
from ..services.llm_service import LLMService
from .dependencies import get_document_service, get_llm_service

router = APIRouter()
logger = get_logger()


@router.post(
  "/generate",
  response_model=GenerateResponse,
  status_code=status.HTTP_200_OK,
  summary="Generate text",
  description="Generate text from the LLM model with the given prompt and parameters",
  responses={
    400: {"model": ErrorResponse, "description": "Bad Request"},
    500: {"model": ErrorResponse, "description": "Internal Server Error"},
  },
)
async def generate_text(
  request: GenerateRequest, llm_service: LLMService = Depends(get_llm_service)
) -> GenerateResponse:
  """Generate text from the LLM model.

  Args:
      request: The generation request with prompt and parameters
      llm_service: Injected LLM service

  Returns:
      GenerateResponse with the generated text and metadata
  """
  logger.info(f"Received generate request for model: {request.model or 'default'}")
  try:
    if request.stream:
      logger.warning("Stream parameter set on non-streaming endpoint")
      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Use /generate/stream endpoint for streaming responses",
      )

    response = await llm_service.generate_text(request)
    logger.info(
      f"Generated {response.tokens_generated} tokens in "
      f"{response.generation_time_ms:.2f}ms using model: {response.model_used}"
    )
    return response
  except ModelNotFoundError as e:
    logger.error(f"Model not found: {e.model_name}")
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=e.to_dict(),
    ) from e
  except ValueError as e:
    logger.error(f"Validation error: {e}")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
  except Exception as e:
    logger.exception("Unexpected error during text generation")
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Failed to generate text: {str(e)}",
    ) from e


@router.post(
  "/generate/stream",
  status_code=status.HTTP_200_OK,
  summary="Generate text with streaming",
  description="Generate text from the LLM model with streaming response",
  responses={
    400: {"model": ErrorResponse, "description": "Bad Request"},
    500: {"model": ErrorResponse, "description": "Internal Server Error"},
  },
)
async def generate_text_stream(
  request: GenerateRequest, llm_service: LLMService = Depends(get_llm_service)
):
  """Generate text from the LLM model with streaming.

  Args:
      request: The generation request with prompt and parameters
      llm_service: Injected LLM service

  Returns:
      Streaming response with generated text chunks
  """
  logger.info(
    f"Received streaming generate request for model: {request.model or 'default'}"
  )
  try:

    async def generate_chunks() -> AsyncGenerator[str, None]:
      """Generate chunks for streaming response."""
      try:
        chunk_count = 0
        async for chunk in llm_service.generate_text_stream(request):
          chunk_count += 1
          yield f"data: {json.dumps({'text': chunk})}\n\n"
        yield "data: [DONE]\n\n"
        logger.info(f"Streaming completed: {chunk_count} chunks sent")
      except ModelNotFoundError as e:
        logger.error(f"Model not found during streaming: {e.model_name}")
        yield f"data: {json.dumps(e.to_dict())}\n\n"
      except Exception as e:
        logger.exception("Error during streaming generation")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
      generate_chunks(),
      media_type="text/event-stream",
      headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
      },
    )
  except ModelNotFoundError as e:
    logger.error(f"Model not found: {e.model_name}")
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=e.to_dict(),
    ) from e
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Failed to generate streaming text: {str(e)}",
    ) from e


@router.get(
  "/health",
  response_model=HealthResponse,
  status_code=status.HTTP_200_OK,
  summary="Health check",
  description="Check the health status of the LLM service",
)
async def health_check(
  llm_service: LLMService = Depends(get_llm_service),
) -> HealthResponse:
  """Check the health of the LLM service.

  Args:
      llm_service: Injected LLM service

  Returns:
      HealthResponse with service status
  """
  logger.debug("Health check requested")
  try:
    is_healthy = await llm_service.check_health()
    model_info = llm_service.get_provider_info()

    status_msg = "healthy" if is_healthy else "unhealthy"
    logger.info(f"Health check result: {status_msg}")

    return HealthResponse(
      status=status_msg,
      model_loaded=is_healthy,
      model_info=model_info if is_healthy else None,
    )
  except Exception as e:
    logger.error(f"Health check failed: {e}")
    return HealthResponse(status="unhealthy", model_loaded=False, model_info=None)


@router.get(
  "/model/info",
  status_code=status.HTTP_200_OK,
  summary="Get model information",
  description="Get information about the currently loaded model",
)
async def get_model_info(llm_service: LLMService = Depends(get_llm_service)) -> dict:
  """Get information about the current model.

  Args:
      llm_service: Injected LLM service

  Returns:
      Dictionary with model information
  """
  logger.debug("Model info requested")
  try:
    info = llm_service.get_provider_info()
    logger.info(f"Model info retrieved: {info.get('model_name', 'unknown')}")
    return info
  except Exception as e:
    logger.exception("Failed to get model info")
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Failed to get model info: {str(e)}",
    ) from e


@router.post(
  "/document/question",
  response_model=GenerateResponse,
  status_code=status.HTTP_200_OK,
  summary="Ask a question about a PDF document",
  description="Upload a PDF file and ask a question about its content",
  responses={
    400: {"model": ErrorResponse, "description": "Bad Request"},
    500: {"model": ErrorResponse, "description": "Internal Server Error"},
  },
)
async def ask_document_question(
  file: UploadFile,
  question: str = Form(..., description="The question to ask about the document"),
  max_tokens: int = Form(
    default=1024, ge=1, le=4096, description="Maximum tokens to generate"
  ),
  temperature: float = Form(
    default=0.7, ge=0.0, le=2.0, description="Sampling temperature"
  ),
  top_p: float = Form(default=0.9, ge=0.0, le=1.0, description="Nucleus sampling"),
  top_k: int = Form(default=40, ge=0, description="Top-k sampling"),
  model: str | None = Form(default=None, description="Model name to use"),
  context_mode: str = Form(
    default="full", description="Context mode: 'full' or 'summary'"
  ),
  document_service: DocumentService = Depends(get_document_service),
) -> GenerateResponse:
  """Ask a question about a PDF document.

  Args:
      file: The PDF file to process
      question: The question to ask about the document
      max_tokens: Maximum number of tokens to generate
      temperature: Sampling temperature
      top_p: Nucleus sampling parameter
      top_k: Top-k sampling parameter
      model: Optional model name to use
      context_mode: How to include context ('full' or 'summary')
      document_service: Injected document service

  Returns:
      GenerateResponse with the answer to the question
  """
  logger.info(
    f"Received document question request: file={file.filename}, "
    f"question={question[:50]}..."
  )

  try:
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
      logger.error(f"Invalid file type: {file.filename}")
      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Only PDF files are supported. Please upload a .pdf file.",
      )

    # Read file content
    file_content = await file.read()
    if not file_content:
      logger.error("Empty file uploaded")
      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Uploaded file is empty",
      )

    logger.info(f"Read {len(file_content)} bytes from {file.filename}")

    # Create request object
    request = DocumentQuestionRequest(
      question=question,
      max_tokens=max_tokens,
      temperature=temperature,
      top_p=top_p,
      top_k=top_k,
      model=model,
      context_mode=context_mode,
    )

    # Process document and generate answer
    response = await document_service.answer_question_about_document(
      request, file_content, file.filename
    )

    logger.success(
      f"Successfully answered question about {file.filename}: "
      f"{response.tokens_generated} tokens generated"
    )
    return response

  except ValueError as e:
    logger.error(f"Validation error: {e}")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
  except ModelNotFoundError as e:
    logger.error(f"Model not found: {e.model_name}")
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=e.to_dict(),
    ) from e
  except Exception as e:
    logger.exception("Unexpected error during document question processing")
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Failed to process document question: {str(e)}",
    ) from e
