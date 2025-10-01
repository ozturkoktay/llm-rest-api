"""Entry point for the AcSYS LLMs REST API application."""

import multiprocessing

from src.config.settings import settings
import uvicorn


def main():
  """Run the FastAPI application."""
  workers = (multiprocessing.cpu_count() * 2) + 1

  uvicorn.run(
    "src.api.app:app",
    host=settings.api_host,
    port=settings.api_port,
    workers=workers,
    loop="uvloop",
    http="httptools",
    reload=False,
    access_log=False,
    use_colors=False,
    server_header=False,
    date_header=False,
    log_level=settings.log_level.lower(),
  )


if __name__ == "__main__":
  main()
