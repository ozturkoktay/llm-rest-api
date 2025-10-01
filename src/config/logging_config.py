"""Logging configuration using Loguru."""

from pathlib import Path
import sys

from loguru import logger

from .settings import settings


class LoggerConfig:
  """Centralized logger configuration."""

  @staticmethod
  def setup() -> None:
    """Configure loguru logger with appropriate handlers and formatting.

    Sets up both console and file logging based on environment settings.
    """
    logger.remove()

    log_format = (
      "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
      "<level>{level: <8}</level> | "
      "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
      "<level>{message}</level>"
    )

    logger.add(
      sys.stdout,
      format=log_format,
      level=settings.log_level,
      colorize=True,
      backtrace=True,
      diagnose=True,
    )

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    logger.add(
      logs_dir / "api_{time:YYYY-MM-DD}.log",
      format=log_format,
      level=settings.log_level,
      rotation="00:00",
      retention="30 days",
      compression="zip",
      backtrace=True,
      diagnose=True,
    )

    logger.add(
      logs_dir / "errors_{time:YYYY-MM-DD}.log",
      format=log_format,
      level="ERROR",
      rotation="00:00",
      retention="90 days",
      compression="zip",
      backtrace=True,
      diagnose=True,
    )

    logger.info(f"Logging configured with level: {settings.log_level}")

  @staticmethod
  def get_logger():
    """Get the configured logger instance.

    Returns:
        The loguru logger instance
    """
    return logger


def get_logger():
  """Get the configured logger instance. Convenience function for dependency injection.

  Returns:
      The loguru logger instance
  """
  return logger
