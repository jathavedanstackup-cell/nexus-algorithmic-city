# syntax=docker/dockerfile:1

# ---------- Stage 1: build the frontend ----------
FROM node:20-slim AS web-build
WORKDIR /web
COPY web/package*.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

# ---------- Stage 2: install Python dependencies ----------
FROM python:3.11-slim AS py-deps
WORKDIR /app
COPY pyproject.toml requirements.txt ./
COPY src/ ./src/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# ---------- Stage 3: runtime ----------
FROM python:3.11-slim AS runtime
WORKDIR /app

RUN useradd --create-home --uid 1000 nexus

COPY --from=py-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=py-deps /usr/local/bin /usr/local/bin
COPY src/ ./src/
COPY --from=web-build /web/dist ./web/dist

ENV PYTHONPATH=/app/src \
    NEXUS_ENV=production \
    PORT=8000

EXPOSE 8000

RUN mkdir -p /app/benchmarks/results && chown -R nexus:nexus /app
USER nexus

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=5 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','8000')+'/health').read()" || exit 1

# Shell form so ${PORT} expands at runtime: container hosts (Render, Railway, Fly,
# Cloud Run) assign a port dynamically and route only to that one.
CMD uvicorn nexus.api.app:app --host 0.0.0.0 --port ${PORT:-8000}
