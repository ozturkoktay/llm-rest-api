# Multi-stage build for LLM API
FROM python:3.12-slim as base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY main.py .
COPY src/ ./src/

RUN pip install --no-cache-dir -e .

RUN useradd -m -u 1000 llmapi && chown -R llmapi:llmapi /app
USER llmapi

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["python", "main.py"]
