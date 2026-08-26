# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base
RUN useradd --create-home --uid 1000 appuser \
    && pip install --no-cache-dir uv
WORKDIR /app

FROM base AS deps-dev
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen

FROM base AS deps-prod
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

# --- Développement : uvicorn avec rechargement à chaud ----------------------
FROM deps-dev AS dev
COPY --chown=appuser:appuser . .
RUN chown -R appuser:appuser /app
USER appuser
ENV PATH="/app/.venv/bin:${PATH}"
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1
# --no-sync : l'environnement a déjà été construit à l'étape précédente ;
# on évite qu'`uv run` ne retente une synchro (et n'échoue en écriture une
# fois passé en utilisateur non-root).
CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# --- Production --------------------------------------------------------------
FROM deps-prod AS production
COPY --chown=appuser:appuser app ./app
RUN chown -R appuser:appuser /app
USER appuser
ENV PATH="/app/.venv/bin:${PATH}"
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1
CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
