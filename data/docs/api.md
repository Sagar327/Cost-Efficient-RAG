# API

GET /health returns service status and the number of stored vectors.

POST /ingest accepts a folder, optional chunk_size, and optional overlap. It loads PDF, HTML, Markdown, and TXT documents, chunks them, embeds them, and upserts them.

POST /retrieve accepts question, k, and an optional source metadata filter. It returns the retrieved chunks, distances, and metadata without calling the language model.

POST /query accepts question, k, and an optional source filter. It performs retrieval and then calls the configured OpenAI-compatible LLM. The response includes the answer, retrieved contexts, retrieval latency, LLM latency, total latency, and token usage when available.

Configuration is read from environment variables through .env. No secrets are hardcoded.
