# Cost-Efficient RAG Demo Document

## Architecture and Ingestion

This sample document is used to demonstrate the Cost-Efficient RAG application.

The application uses ChromaDB as a local persistent vector store. ChromaDB was selected because it is lightweight, easy to run locally, and suitable for a lightly queried document index.

Documents are split into configurable chunks before embedding. The default chunk size is 900 characters with 120 characters of overlap. Overlap helps preserve context across chunk boundaries.

Ingestion is idempotent. Each chunk receives a deterministic SHA-256-derived identifier based on the source, chunk index, and chunk text. Chunks are written with upsert rather than add, so ingesting the same document repeatedly does not create duplicate vectors.

Each stored chunk includes metadata such as source, chunk_index, start_char, and end_char. The source metadata can be used as a retrieval filter.

## Embeddings

The embedding model is sentence-transformers/all-MiniLM-L6-v2. It produces 384-dimensional embeddings. Embeddings are normalized before insertion and query.

## Retrieval and Answer Generation

The application accepts a question and a configurable top-k value. It retrieves the most relevant chunks from the vector store and passes those chunks to the language model.

The answer prompt is grounded. The model is instructed to use only the retrieved context, cite supporting chunks as [1], [2], and avoid inventing facts or citations.

If the retrieved context does not contain enough evidence, the system should respond:

"I don't have enough relevant context to answer that."

## API

The application exposes HTTP endpoints through FastAPI.

GET /health returns service status and the number of stored vectors.

POST /ingest accepts a document folder and optional chunk size and overlap.

POST /retrieve performs vector retrieval and returns the retrieved chunks, distances, and metadata without calling the language model.

POST /query performs retrieval followed by grounded answer generation. The response includes the answer, retrieved contexts, retrieval latency, LLM latency, total latency, and token usage when available.

## Evaluation

The evaluation harness uses a fixed set of 15 questions.

Retrieval quality is measured using Recall@k, Hit Rate, MRR, nDCG, and context precision.

Answer quality is evaluated using keyword F1 and citation grounding as automated proxies. These are proxies rather than human-validated faithfulness scores.

The system also measures retrieval and end-to-end latency.

## Cost-Efficiency Goal

The project compares the cost of a local ChromaDB deployment with a managed vector database assumption at 100,000, 1,000,000, and 10,000,000 vectors.

The main trade-off is that a local vector store can reduce infrastructure cost for a lightly queried index, while managed infrastructure may be preferable when high availability, scaling, operational simplicity, or heavy query traffic becomes more important.
