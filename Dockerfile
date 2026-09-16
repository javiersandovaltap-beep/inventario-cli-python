# Dockerfile for inventario-cli-python
# Multi-stage build: builder verifies imports, runtime is minimal.
# Stage 1 (builder): copy source, verify imports work (build verification).
# Stage 2 (runtime): minimal image, no dev tooling, runs as non-root.
# Base image: python:3.12-slim per AGENTS.md section 2 (Stack).
# Image size target: < 200MB (python:3.12-slim ~45MB + app code ~100KB).
# Real tests in builder stage: deferred to Fase 4 when tests/ exists.

# === Stage 1: builder ===
FROM python:3.12-slim AS builder

WORKDIR /app

# Copy project files. .dockerignore filters out caches, .venv, .git, etc.
COPY pyproject.toml ./
COPY modulos/ ./modulos/
COPY presets/ ./presets/
COPY main.py ./
COPY data/ ./data/

# Build verification: importing main transitively pulls in modulos/* and
# presets/*. If any import fails, the build fails. pytest in builder stage
# is deferred to Fase 4 (tests/ does not exist yet).
RUN python -c "import main; print('main module imports OK')"

# === Stage 2: runtime ===
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy verified application code from builder stage.
COPY --from=builder /app/ /app/

# Run as non-root user for security (container hardening baseline).
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# Default entrypoint: run the CLI.
# Override examples:
#   docker run --rm inventario:dev pytest                    (Fase 4+)
#   docker run --rm -it -v "${PWD}/data:/app/data" inventario:dev
ENTRYPOINT ["python", "main.py"]
