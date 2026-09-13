FROM python:3.11-slim AS base

# System deps: build tools for faiss/sentence-transformers wheels that need them,
# plus curl for the HEALTHCHECK below.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the sentence-transformers embedding model at BUILD time.
# Without this, the first request (or the startup auto-bootstrap) would try
# to reach huggingface.co at runtime — which may be blocked or slow in a
# production network, and would otherwise turn "first search after deploy"
# into a multi-second-to-failing cold start.
ARG EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('${EMBEDDING_MODEL_NAME}')"

COPY app ./app
COPY scripts ./scripts
COPY data/raw ./seed_data/raw
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# data/ is expected to be a mounted volume in production (see docker-compose.yml)
# so the sqlite DB, FAISS index, and KB version snapshots survive restarts/redeploys.
RUN mkdir -p data/raw data/processed data/embeddings data/kb_versions

ENV PYTHONUNBUFFERED=1 \
    PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://localhost:${PORT}/health || exit 1

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
