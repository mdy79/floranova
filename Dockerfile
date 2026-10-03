FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for ultra-fast dependency management
COPY --from=ghcr.io/astral-sh/uv:0.12.17 /uv /uvx /bin/

# Copy dependency definition
COPY pyproject.toml uv.lock ./

# Install project dependencies
RUN uv pip install --system -r <(uv export --no-dev --format requirements-txt) || uv pip install --system fastapi "sqlalchemy>=2.0" aiosqlite "pydantic>=2.0" pydantic-settings "python-jose[cryptography]" email-validator greenlet jinja2 jdatetime python-multipart bcrypt uvicorn

# Copy application source code
COPY src/ /app/src/
COPY README.md /app/

RUN uv pip install --system -e .

EXPOSE 8000

CMD ["uvicorn", "floranova.main:app", "--host", "0.0.0.0", "--port", "8000"]
