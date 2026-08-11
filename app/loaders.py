from pathlib import Path
from pypdf import PdfReader
from bs4 import BeautifulSoup

def load_file(path: str) -> str:
    p = Path(path)
    ext = p.suffix.lower()
    if ext in {".txt", ".md", ".markdown"}:
        return p.read_text(encoding="utf-8", errors="ignore")
    if ext in {".html", ".htm"}:
        return BeautifulSoup(p.read_text(encoding="utf-8", errors="ignore"), "html.parser").get_text("\n")
    if ext == ".pdf":
        reader = PdfReader(str(p))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    raise ValueError(f"Unsupported file type: {p.suffix}. Use PDF/HTML/MD/TXT.")

def iter_documents(folder: str):
    root = Path(folder)
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in {".pdf", ".html", ".htm", ".md", ".markdown", ".txt"}:
            yield p
