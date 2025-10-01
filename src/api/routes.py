"""API routes for the LLM service.

Following RESTful principles and clean architecture.
"""

from collections.abc import AsyncGenerator
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from ..config.logging_config import get_logger
from ..exceptions import ModelNotFoundError
from ..models.schemas import (
  ErrorResponse,
  GenerateRequest,
  GenerateResponse,
  HealthResponse,
)
from ..services.llm_service import LLMService
from .dependencies import get_llm_service

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
