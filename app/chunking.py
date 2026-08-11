import re
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

@dataclass
class Chunk:
    id: str
    text: str
    source: str
    chunk_index: int
    start_char: int
    end_char: int

def normalize(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def chunk_text(text: str, source: str, chunk_size: int = 900, overlap: int = 120):
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be > 0 and overlap must be >= 0 and < chunk_size")
    text = normalize(text)
    if not text:
        return []
    chunks, start, idx = [], 0, 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        if end < len(text):
            # Prefer a natural boundary.
            candidates = [text.rfind("\n\n", start, end), text.rfind(". ", start, end),
                          text.rfind(" ", start, end)]
            boundary = max(candidates)
            if boundary > start + int(chunk_size * 0.55):
                end = boundary + (2 if text[boundary:boundary+2] == "\n\n" else 1)
        piece = text[start:end].strip()
        if piece:
            raw_id = f"{source}|{idx}|{piece}"
            cid = sha256(raw_id.encode("utf-8")).hexdigest()[:24]
            chunks.append(Chunk(cid, piece, source, idx, start, end))
            idx += 1
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks
