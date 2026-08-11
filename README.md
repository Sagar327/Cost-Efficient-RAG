# Cost-Efficient RAG

A lightweight Retrieval-Augmented Generation (RAG) application built to demonstrate that a local vector store can provide a practical, low-cost alternative to fully managed vector databases for lightly queried document collections.

The system supports document ingestion, semantic retrieval, grounded LLM answers, evaluation, latency tracking, and cost analysis.

## Overview

This project was built for the **Cost-Efficient RAG** assignment, with the following goals:

- Build a working end-to-end RAG application
- Use a low-cost vector store
- Make ingestion configurable and idempotent
- Measure retrieval quality using real IR metrics
- Evaluate generated answers
- Track latency and token usage
- Compare estimated costs at different vector scales

## Key Features

- PDF, HTML, Markdown, and TXT ingestion
- Configurable chunk size and overlap
- Idempotent document re-ingestion
- Persistent local ChromaDB vector store
- `all-MiniLM-L6-v2` embeddings
- 384-dimensional embeddings
- Configurable Top-K retrieval
- Metadata filtering by source
- Grounded LLM responses with chunk citations
- No-context fallback to reduce hallucination
- FastAPI backend
- Browser-based UI
- Retrieval and generation latency tracking
- Token usage logging
- Retrieval evaluation with Recall@k, Hit Rate, MRR, nDCG, and Context Precision
- Answer evaluation
- Cost comparison for 100K, 1M, and 10M vectors

## Architecture

```text
                    User
                      |
                      v
              +---------------+
              |    Web UI     |
              | HTML/CSS/JS   |
              +-------+-------+
                      |
                      v
              +---------------+
              |    FastAPI    |
              |    Backend    |
              +-------+-------+
                      |
          +-----------+-----------+
          |                       |
          v                       v
   +-------------+        +---------------+
   |   ChromaDB  |        | OpenAI-       |
   | Local Store |        | Compatible LLM|
   +------+------+        +---------------+
          |
          v
   +-------------+
   | Embeddings  |
   | MiniLM-L6-v2|
   | 384 dims    |
   +-------------+
```

## Why ChromaDB?

ChromaDB was selected because this project targets a potentially large but lightly queried index.

A persistent local ChromaDB deployment provides:

- Low infrastructure cost
- No always-on managed vector database
- Simple local development
- Persistent vector storage
- Metadata filtering
- Upsert support for idempotent ingestion

The trade-off is that backups, high availability, scaling, and operational maintenance remain the responsibility of the application owner.

## Project Structure

```text
cost_efficient_rag/
│
├── app/
│   ├── chunking.py       # Document chunking
│   ├── config.py         # Environment configuration
│   ├── ingest.py         # Document ingestion
│   ├── llm.py            # LLM interaction
│   ├── loaders.py        # PDF/HTML/MD/TXT loaders
│   ├── main.py           # FastAPI application
│   ├── rag.py            # Retrieval and RAG pipeline
│   └── vectorstore.py    # ChromaDB integration
│
├── data/docs/            # Sample document corpus
├── eval/
│   ├── answer_eval.py    # Answer evaluation
│   ├── evaluate.py       # Retrieval evaluation
│   └── questions.json    # 15 evaluation questions
│
├── reports/              # Query logs and generated reports
├── scripts/
│   └── cost_analysis.py  # Cost comparison
├── tests/                # Unit tests
├── ui/
│   └── index.html        # Web interface
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Create the environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure `.env`

Create a `.env` file using `.env.example`.

Example local configuration:

```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

LLM_API_KEY=
LLM_MODEL=gemma3:4b
LLM_BASE_URL=http://localhost:11434/v1

CHROMA_PATH=./storage/chroma
COLLECTION_NAME=rag_chunks

DEFAULT_CHUNK_SIZE=900
DEFAULT_CHUNK_OVERLAP=120

DEFAULT_TOP_K=5
MAX_TOP_K=20
```

The embedding model runs locally.

The example configuration uses **Ollama + Gemma 3 4B** as the local LLM.

### 4. Start the LLM

Make sure Ollama is running:

```bash
ollama run gemma3:4b
```

### 5. Ingest documents

```bash
python -m app.ingest data/docs
```

Default chunking:

```text
Chunk size : 900 characters
Overlap    : 120 characters
```

Custom values can be provided:

```bash
python -m app.ingest data/docs --chunk-size 900 --overlap 120
```

### 6. Start the API

```bash
uvicorn app.main:app --reload
```

Open:

- **Web UI:** `http://127.0.0.1:8000/`
- **API docs:** `http://127.0.0.1:8000/docs`

## How It Works

```text
Documents
   ↓
Load & Extract Text
   ↓
Chunk Documents
   ↓
Generate Embeddings
   ↓
Store in ChromaDB
   ↓
User Question
   ↓
Question Embedding
   ↓
Top-K Retrieval
   ↓
Grounded Context
   ↓
LLM
   ↓
Answer + Citations
```

## Ingestion

The ingestion pipeline supports:

- PDF
- HTML
- Markdown
- TXT

Each chunk contains metadata including:

```text
source
chunk_index
start_char
end_char
```

The `source` metadata can be used as a retrieval filter.

### Idempotent Re-ingestion

Chunk IDs are generated deterministically from the source, chunk index, and chunk content.

ChromaDB `upsert` is then used instead of `add`.

Therefore, running ingestion multiple times does not create duplicate vectors.

Example:

```text
First run:
6 files
14 chunks upserted
21 total vectors

Second run:
6 files
14 chunks upserted
21 total vectors
```

The vector count remains stable.

## Retrieval

The system performs semantic Top-K retrieval.

Example request:

```json
{
  "question": "What embedding model is used?",
  "k": 5
}
```

A source filter can also be supplied:

```json
{
  "question": "What embedding model is used?",
  "k": 5,
  "source": "architecture.md"
}
```

## Grounded Generation

Retrieved chunks are passed to the LLM as context.

The generation prompt instructs the model to:

- Answer using the retrieved evidence
- Cite the chunks it uses
- Avoid unsupported information
- Return a clear fallback when relevant evidence is unavailable

Example:

```text
The embedding model is
sentence-transformers/all-MiniLM-L6-v2 [1].
```

If there is insufficient context:

```text
I don't have enough relevant context to answer that.
```

## Evaluation

The project uses a fixed set of **15 questions** located in:

```text
eval/questions.json
```

### Retrieval Metrics

The retrieval evaluation measures:

- Recall@k
- Hit Rate
- MRR
- nDCG
- Context Precision

Run:

```bash
python eval/evaluate.py 3
python eval/evaluate.py 5
python eval/evaluate.py 8
```

This allows different Top-K configurations to be compared.

### Answer Evaluation

Answer evaluation is implemented in:

```text
eval/answer_eval.py
```

Run:

```bash
python eval/answer_eval.py
```

The evaluation focuses on whether generated answers are supported by the retrieved context and whether they address the question.

## Latency & Logging

Each query records:

- Retrieval latency
- LLM latency
- Total latency
- Retrieved chunk count
- Retrieved chunk IDs
- Token usage when provided by the LLM

Logs are written to:

```text
reports/query_log.jsonl
```

This allows query performance to be analyzed after running the application.

## Cost Analysis

The project includes a cost-analysis script:

```bash
python scripts/cost_analysis.py
```

The comparison considers:

```text
100K vectors
1M vectors
10M vectors
```

The managed-vector-database figures are **scenario assumptions**, not vendor quotations.

The purpose is to compare the cost characteristics of local vector storage against always-on managed vector infrastructure.

## Design Trade-offs

### Strengths

- Low infrastructure cost
- Simple architecture
- Local embeddings
- Persistent vector storage
- Idempotent ingestion
- Metadata filtering
- Measurable retrieval quality
- Query-level performance logging

### Limitations

- Local storage requires manual operational management
- No built-in high availability
- Backups must be handled separately
- Scaling requires additional infrastructure
- Local LLM latency depends on available hardware
- Embedding quality depends on the selected model

## When Would I Use a Managed Vector Database?

I would consider switching back to a managed vector database when operational requirements become more important than infrastructure cost.

Examples include:

- High query concurrency
- Strict availability requirements
- Distributed deployments
- Automatic backups
- Disaster recovery
- Multi-node scaling
- Large production workloads
- Reduced operational overhead

For a small or lightly queried corpus, the local ChromaDB approach provides a simpler and more cost-efficient architecture.

## Requirement Coverage

| Requirement | Implementation |
|---|---|
| PDF / HTML / MD ingestion | `app/loaders.py` |
| Configurable chunking | `app/chunking.py` |
| Idempotent ingestion | Deterministic IDs + ChromaDB `upsert` |
| Embeddings | Sentence Transformers |
| 384-dimensional vectors | `all-MiniLM-L6-v2` |
| Vector store | ChromaDB |
| Metadata filter | `source` |
| Top-K retrieval | Configurable `k` |
| Grounded answers | `app/rag.py` + `app/llm.py` |
| Chunk citations | `[1]`, `[2]`, etc. |
| No-context fallback | Grounded prompt |
| HTTP API | FastAPI |
| Environment configuration | `.env` |
| Latency logging | `reports/query_log.jsonl` |
| Retrieval evaluation | `eval/evaluate.py` |
| Answer evaluation | `eval/answer_eval.py` |
| Cost analysis | `scripts/cost_analysis.py` |

## Reproduce the Project

```bash
# Create environment
python -m venv .venv

# Activate
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure .env

# Start local LLM
ollama run gemma3:4b

# Ingest documents
python -m app.ingest data/docs

# Start API
uvicorn app.main:app --reload

# Run retrieval evaluation
python eval/evaluate.py 5

# Run answer evaluation
python eval/answer_eval.py

# Run cost analysis
python scripts/cost_analysis.py
```

## Notes

- `.env` should never be committed.
- `storage/` contains generated ChromaDB data and is excluded from Git.
- The embedding model is downloaded on first use.
- Ollama must be running when using the local LLM configuration.
- Evaluation results depend on the evaluation dataset and configured LLM.
- Cost estimates depend on the assumptions defined in the cost-analysis script.

## License

This project is intended for educational, experimental, and placement evaluation purposes.
