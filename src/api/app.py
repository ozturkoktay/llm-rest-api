"""Main FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..config.logging_config import LoggerConfig, get_logger
from ..config.settings import settings
from .routes import router

LoggerConfig.setup()
logger = get_logger()


@asynccontextmanager
async def lifespan(app):  # noqa: ARG001
  """Application lifespan manager."""
  logger.info("Starting LLM API service...")
  yield
  logger.info("Shutting down LLM API service...")


def create_app() -> FastAPI:
  """Create and configure the FastAPI application.

  Factory pattern for application creation.
  """
  app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
  )

  if settings.cors_enabled:
    app.add_middleware(
      CORSMiddleware,
      allow_origins=settings.cors_origins,
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
    )

  app.include_router(router, prefix="/api/v1", tags=["LLM"])

  @app.get("/", tags=["Root"])
  async def root():
    """Root endpoint with API information."""
    return JSONResponse(
      {
        "message": "LLM API Service",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/api/v1/health",
      }
    )

  return app


app = create_app()
