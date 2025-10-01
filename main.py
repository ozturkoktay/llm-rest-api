"""Entry point for the AcSYS LLMs REST API application."""

from src.config.settings import settings
import uvicorn


def main():
  """Run the FastAPI application."""
  uvicorn.run(
    "src.api.app:app",
    host=settings.api_host,
    port=settings.api_port,
    workers=8,
    loop="uvloop",
    http="httptools",
    reload=True,
    log_level=settings.log_level.lower(),
    access_log=False,
    use_colors=False,
    server_header=False,
    date_header=False,
  )


if __name__ == "__main__":
  main()
