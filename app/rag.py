import time
import json
from pathlib import Path
from datetime import datetime, timezone
from sentence_transformers import SentenceTransformer
from .config import settings
from .vectorstore import ChromaStore
from .llm import generate_answer

_embedding_model = None
_store = None

def get_store():
    global _embedding_model, _store
    if _store is None:
        _embedding_model = SentenceTransformer(settings.embedding_model)
        _store = ChromaStore(settings.chroma_path, settings.collection_name, _embedding_model)
    return _store

def retrieve(question: str, k: int | None = None, source: str | None = None):
    k = k or settings.default_top_k
    k = min(max(1, k), settings.max_top_k)
    raw = get_store().query(question, k=k, source=source)
    docs = raw["documents"][0] if raw["documents"] else []
    metas = raw["metadatas"][0] if raw["metadatas"] else []
    dists = raw["distances"][0] if raw["distances"] else []
    ids = raw["ids"][0] if raw["ids"] else []
    return [
        {"id": ids[i], "text": docs[i], "source": metas[i]["source"],
         "chunk_index": metas[i]["chunk_index"], "distance": dists[i]}
        for i in range(len(docs))
    ]

def answer(question: str, k: int | None = None, source: str | None = None):
    t0 = time.perf_counter()
    contexts = retrieve(question, k, source)
    retrieval_ms = (time.perf_counter() - t0) * 1000
    text, llm_ms, usage = generate_answer(
        question, contexts, settings.llm_base_url, settings.llm_api_key, settings.llm_model
    )
    result = {
        "answer": text,
        "contexts": contexts,
        "retrieval_ms": round(retrieval_ms, 2),
        "llm_ms": round(llm_ms, 2),
        "total_ms": round(retrieval_ms + llm_ms, 2),
        "usage": usage,
    }
    Path("reports").mkdir(exist_ok=True)
    log_row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "k": len(contexts),
        "chunk_ids": [c["id"] for c in contexts],
        "retrieval_ms": result["retrieval_ms"],
        "llm_ms": result["llm_ms"],
        "total_ms": result["total_ms"],
        "usage": usage,
    }
    with open("reports/query_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_row, ensure_ascii=False) + "\n")
    return result
