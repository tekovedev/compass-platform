# Compass Platform

RAG API built on FastAPI and AWS Bedrock Knowledge Bases.

## Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- AWS credentials configured (`aws configure` or environment variables)
- A Bedrock Knowledge Base already provisioned

## Local setup

```bash
# Install dependencies
poetry install

# Configure environment
cp .env.example .env
# Edit .env and set KNOWLEDGE_BASE_ID (and optionally OPENSEARCH_ENDPOINT)
```

## Run the API

```bash
poetry run uvicorn compass.api.app:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Test it:

```bash
curl http://localhost:8000/api/v1/healthcheck
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/healthcheck` | Health check (public) |
| POST | `/api/v1/query` | Ask a question against the knowledge base |

### Query

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "your question here", "top_k": 5}'
```

Data ingestion/sync for the Knowledge Base is managed from the `compass-knowledge-hub` repository.

## Authentication

Auth is disabled by default. To enable it, set `COGNITO_USER_POOL_ID` and `COGNITO_CLIENT_ID` in `.env`. Once set, all endpoints except `/healthcheck` require a Bearer JWT from Cognito.

## Run with Docker

```bash
docker build -t compass-platform .
docker run -p 8000:8000 --env-file .env compass-platform
```

## Tests

```bash
poetry run pytest tests/ -v
```
