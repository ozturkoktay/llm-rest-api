"""Centralized configuration management."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  """Application settings."""

  api_title: str = "AcSYS LLMs REST API"
  api_version: str = "1.0.0"
  api_description: str = "Professional REST API for Local LLM Models"
  api_host: str = "0.0.0.0"  # noqa: S104
  api_port: int = 8001

  model_path: str = ""
  model_type: str = "ollama"
  model_name: str = "llama2"

  ollama_base_url: str = "http://localhost:11434"

  max_concurrent_requests: int = 10
  request_timeout: int = 300

  cors_enabled: bool = True
  cors_origins: list = ["*"]

  log_level: str = "INFO"

  model_config = SettingsConfigDict(
    env_file=".env", env_file_encoding="utf-8", case_sensitive=False
  )


settings = Settings()
