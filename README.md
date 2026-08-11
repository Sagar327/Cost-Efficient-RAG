# Cost-Efficient RAG Application

A submission-ready reference implementation for Problem 1 of the Applied AI / ML Engineering take-home.

## What is implemented

- PDF / HTML / Markdown / TXT ingestion
- configurable chunk size + overlap
- deterministic chunk IDs + Chroma `upsert` for idempotent re-ingest
- local persistent Chroma vector store
- 384-dim local SentenceTransformer embeddings
- top-k retrieval with configurable `k`
- metadata filter by `source`
- grounded LLM answer with citations and an explicit no-context fallback
- FastAPI endpoints
- per-query retrieval/LLM/total latency
- LLM token usage logging when provider returns it
- 15-question retrieval benchmark
- Recall@k, Hit Rate, MRR, nDCG, Context Precision
- assumption-based cost comparison at 100K / 1M / 10M vectors
- configurable secrets via `.env`

Chroma's Python API supports a persistent local client, metadata-filtered similarity search, and `upsert`, which is why it is a good fit for a small/lightly queried index. See the official Chroma docs: https://docs.trychroma.com/ (PersistentClient and collection upsert/query are documented there).

## 1. Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
```

The first run downloads the embedding model.

Set an OpenAI-compatible LLM in `.env`:

```text
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=YOUR_KEY
LLM_MODEL=gpt-4o-mini
```

Or use a local OpenAI-compatible server such as Ollama:

```text
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=
LLM_MODEL=YOUR_LOCAL_MODEL
```

## 2. Ingest

```bash
python -m app.ingest data/docs --chunk-size 900 --overlap 120
```

Run it twice. The vector count should remain stable because chunk IDs are deterministic and the store uses upsert.

## 3. Start API

```bash
uvicorn app.main:app --reload
```

Open the interactive API docs at `/docs`.

Example:

```bash
curl -X POST http://127.0.0.1:8000/query ^
  -H "Content-Type: application/json" ^
  -d "{"question":"Why is ingestion idempotent?","k":5}"
```

For Linux/macOS use `\` instead of `^`.

Metadata filter example:

```json
{"question":"What is the chunk size?","k":5,"source":"architecture.md"}
```

## 4. Retrieval evaluation

First ingest the sample corpus, then:

```bash
python eval/evaluate.py 5
```

Run different k values:

```bash
python eval/evaluate.py 3
python eval/evaluate.py 5
python eval/evaluate.py 8
```

Record the resulting metrics in your final report. Do not invent numbers.

## 5. Cost comparison

```bash
python scripts/cost_analysis.py
```

This creates `reports/cost_comparison.csv`.

Important: the managed-store numbers are explicitly scenario assumptions, not vendor quotes. Replace them with the provider you would actually deploy if asked for a production estimate.

## 6. Design decisions

### Why Chroma?

For this assignment the workload is a lightly queried index where always-on managed vector infrastructure can dominate cost. Chroma can persist locally, which keeps the architecture simple and avoids a separate vector service. The trade-off is that the local deployment is responsible for backups, high availability, scaling and operations.

### Why local embeddings?

`all-MiniLM-L6-v2` is small and runs locally, so ingestion does not require a second paid embedding API. The downside is that embedding quality may be below a larger hosted embedding model.

### Why deterministic IDs?

A chunk ID is derived from source + chunk index + chunk text. Re-ingesting unchanged documents therefore addresses the same records. `upsert` updates changed records instead of creating duplicates.

### Why retrieval metrics?

A good answer can hide poor retrieval. Recall@k, MRR, nDCG and context precision expose retrieval quality independently of the LLM.

### Weak link / when to switch back to managed

The weak link is operational scale. A local persistent store is excellent for a small, lightly queried corpus, but managed infrastructure becomes attractive when uptime, concurrency, multi-node scaling, backups, and operational simplicity matter more than the lowest fixed cost.

## 7. Submission checklist

- [ ] `.env` is NOT committed
- [ ] `storage/` is NOT committed
- [ ] Run ingestion twice and record stable vector count
- [ ] Run retrieval evaluation for k=3,5,8
- [ ] Run 15 answer questions and save representative outputs
- [ ] Report p50/p95 latency from actual runs
- [ ] Report token usage from actual runs
- [ ] Run cost analysis and explain assumptions
- [ ] Include one screenshot of `/docs` and one sample grounded answer
- [ ] Mention limitations honestly

## Suggested report structure

1. Architecture
2. Chunking and ingestion
3. Retrieval design
4. Answer grounding
5. Retrieval evaluation
6. Answer evaluation
7. Cost analysis
8. Trade-offs / weak link
9. How to reproduce

## Scoring alignment

| Requirement | Implementation |
|---|---|
| PDF/HTML/MD | `app/loaders.py` |
| configurable chunks | `app/chunking.py`, CLI/API |
| idempotent ingest | deterministic IDs + `upsert` |
| embeddings | SentenceTransformer |
| vector + metadata | Chroma |
| metadata filter | `source` in `/retrieve` and `/query` |
| top-k | `k` parameter |
| grounded answer | `app/llm.py` |
| no-context behavior | explicit fallback in system prompt |
| HTTP endpoint | FastAPI |
| env config | `.env` |
| latency/chunks/tokens | API response + logs/usage |
| Recall/Hit/MRR/nDCG/context precision | `eval/evaluate.py` |
| 15–30 questions | `eval/questions.json` has 15 |
| cost at scale | `scripts/cost_analysis.py` |
