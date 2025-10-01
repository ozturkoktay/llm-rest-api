"""Request and response models for the API."""

from pydantic import BaseModel, Field, field_validator


class GenerateRequest(BaseModel):
  """Request model for text generation."""

  prompt: str = Field(..., description="The input prompt for the model")
  max_tokens: int = Field(
    default=512, ge=1, le=4096, description="Maximum number of tokens to generate"
  )
  temperature: float = Field(
    default=0.7, ge=0.0, le=2.0, description="Sampling temperature for generation"
  )
  top_p: float = Field(
    default=0.9, ge=0.0, le=1.0, description="Nucleus sampling parameter"
  )
  top_k: int = Field(default=40, ge=0, description="Top-k sampling parameter")
  stop_sequences: list[str] | None = Field(
    default=None, description="List of sequences that will stop generation"
  )
  stream: bool = Field(default=False, description="Whether to stream the response")
  model: str | None = Field(
    default=None, description="Model name to use for generation (overrides default)"
  )

  @field_validator("prompt")
  @classmethod
  def prompt_must_not_be_empty(cls, v: str) -> str:
    """Validate that prompt is not empty."""
    if not v or not v.strip():
      raise ValueError("Prompt cannot be empty")
    return v


class GenerateResponse(BaseModel):
  """Response model for text generation."""

  generated_text: str = Field(..., description="The generated text")
  prompt: str = Field(..., description="The original prompt")
  model_used: str = Field(..., description="Model name that was used for generation")
  tokens_generated: int = Field(..., description="Number of tokens generated")
  finish_reason: str = Field(
    ..., description="Reason for generation completion (length, stop, etc.)"
  )
  generation_time_ms: float = Field(
    ..., description="Time taken to generate in milliseconds"
  )


class HealthResponse(BaseModel):
  """Response model for health check."""

  status: str = Field(..., description="Health status of the service")
  model_loaded: bool = Field(..., description="Whether a model is loaded")
  model_info: dict | None = Field(
    default=None, description="Information about the loaded model"
  )


class ErrorResponse(BaseModel):
  """Response model for errors."""

  error: str = Field(..., description="Error message")
  detail: str | None = Field(default=None, description="Detailed error information")
