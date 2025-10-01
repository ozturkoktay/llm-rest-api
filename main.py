"""Entry point for the LLM API application."""

from src.config.settings import settings
import uvicorn


def main():
  """Run the FastAPI application."""
  uvicorn.run(
    "src.api.app:app",
    host=settings.api_host,
    port=settings.api_port,
    reload=True,
    log_level=settings.log_level.lower(),
  )


if __name__ == "__main__":
  main()
