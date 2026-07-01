# BSM API — multi-stage Docker build
# Stage 1: builder (installs dependencies with uv)
# Stage 2: development (with reload)
# Stage 3: production (minimal, no shell)

FROM python:3.12-slim AS base
WORKDIR /workspace

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy workspace configuration first (layer cache optimisation).
# All workspace member pyproject.toml files are needed for uv to resolve the
# full dependency graph before copying application source.
COPY pyproject.toml uv.lock ./
COPY shared/ shared/
COPY apps/api/pyproject.toml apps/api/
COPY apps/workers/pyproject.toml apps/workers/

# ---------------------------------------------------------------------------
# Builder: install all dependencies
# ---------------------------------------------------------------------------
FROM base AS builder
COPY . .

RUN uv sync --frozen --no-dev --all-packages

# ---------------------------------------------------------------------------
# Development: full workspace with hot-reload
#
# The compose volume mount (.:/workspace) overlays the image at runtime,
# replacing the build-time .venv with the host macOS venv (which the Linux
# container cannot use). We therefore install into UV_PROJECT_ENVIRONMENT=/opt/venv
# (outside the mounted path) so the venv survives the mount and is always usable.
# ---------------------------------------------------------------------------
FROM base AS development

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install with dev dependencies; writes into /opt/venv, not /workspace/.venv
COPY . .
RUN uv sync --frozen --all-packages

EXPOSE 8000

# Run from apps/api so that app.main resolves correctly.
# uv run uses UV_PROJECT_ENVIRONMENT=/opt/venv automatically.
CMD ["uv", "run", "--directory", "/workspace/apps/api", "uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--reload", \
     "--reload-dir", "/workspace/apps/api/app", \
     "--reload-dir", "/workspace/shared"]

# ---------------------------------------------------------------------------
# Production: distroless-like minimal image
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS production

# Create non-root user
RUN groupadd --gid 1001 bsm && \
    useradd --uid 1001 --gid bsm --no-create-home bsm

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /workspace/.venv /app/.venv

# Copy application source
COPY --chown=bsm:bsm shared/ /app/shared/
COPY --chown=bsm:bsm engines/ /app/engines/
COPY --chown=bsm:bsm reasoning/ /app/reasoning/
COPY --chown=bsm:bsm data/ /app/data/
COPY --chown=bsm:bsm reports/ /app/reports/
COPY --chown=bsm:bsm workflow/ /app/workflow/
COPY --chown=bsm:bsm observability/ /app/observability/
COPY --chown=bsm:bsm apps/api/app/ /app/app/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER bsm

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
