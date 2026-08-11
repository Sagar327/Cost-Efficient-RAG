import argparse
from pathlib import Path
from .config import settings
from .chunking import chunk_text
from .loaders import load_file, iter_documents
from .rag import get_store

def ingest(folder: str, chunk_size: int | None = None, overlap: int | None = None):
    chunk_size = chunk_size or settings.default_chunk_size
    overlap = settings.default_chunk_overlap if overlap is None else overlap
    all_chunks = []
    root = Path(folder)
    for p in iter_documents(folder):
        text = load_file(str(p))
        source = str(p.relative_to(root)).replace("\\", "/")
        all_chunks.extend(chunk_text(text, source, chunk_size, overlap))
    get_store().upsert(all_chunks)
    return {"files": len(list(iter_documents(folder))), "chunks_upserted": len(all_chunks), "total_vectors": get_store().count()}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--chunk-size", type=int)
    ap.add_argument("--overlap", type=int)
    args = ap.parse_args()
    print(ingest(args.folder, args.chunk_size, args.overlap))
