# Architecture and ingestion

This sample corpus describes the Cost-Efficient RAG reference implementation.

The baseline chunk size is 900 characters with 120 characters of overlap. Chunk size and overlap are configurable at ingestion time. Overlap helps preserve context across chunk boundaries.

The implementation uses Chroma as a local persistent vector store. It uses Chroma PersistentClient so vectors survive process restarts. The store is intentionally local because this project targets a lightly queried index.

Ingestion uses deterministic SHA-256-derived chunk IDs based on source, chunk index, and chunk text. Chunks are written with upsert rather than add, making repeated ingestion idempotent and preventing duplicate vectors.

Each chunk stores metadata: source, chunk_index, start_char, and end_char. The source metadata can be used as a metadata filter during retrieval.

The embedding model is sentence-transformers/all-MiniLM-L6-v2. It produces 384-dimensional embeddings. Embeddings are normalized before insertion and query.

The answer prompt is grounded: it tells the language model to use only retrieved context, cite chunks as [1], [2], and say "I don't have enough relevant context to answer that." when evidence is insufficient.
