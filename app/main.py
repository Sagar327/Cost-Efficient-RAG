from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .config import settings
from .ingest import ingest
from .rag import answer, retrieve, get_store


app = FastAPI(
    title="Cost-Efficient RAG",
    version="1.0.0"
)


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------

@app.get("/", include_in_schema=False)
def ui():
    return FileResponse("ui/index.html")


# ---------------------------------------------------------
# Request models
# ---------------------------------------------------------

class IngestRequest(BaseModel):
    folder: str = "data/docs"
    chunk_size: int | None = Field(default=None, gt=0)
    overlap: int | None = Field(default=None, ge=0)


class QueryRequest(BaseModel):
    question: str = Field(min_length=2)
    k: int = Field(
        default=settings.default_top_k,
        ge=1,
        le=settings.max_top_k
    )
    source: str | None = None


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "vectors": get_store().count()
    }


# ---------------------------------------------------------
# Upload + automatic ingestion
# ---------------------------------------------------------

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    """
    Upload a PDF/HTML/MD/TXT document into data/docs
    and automatically ingest it into the vector store.
    """

    allowed_extensions = {
        ".pdf",
        ".html",
        ".htm",
        ".md",
        ".txt"
    }

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was selected."
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Please upload PDF, HTML, MD, or TXT."
            )
        )

    docs_dir = Path("data/docs")
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Keep only the filename so a client cannot
    # provide an arbitrary filesystem path.
    safe_name = Path(file.filename).name

    destination = docs_dir / safe_name

    try:
        contents = await file.read()
        destination.write_bytes(contents)

        # Re-ingest the folder.
        # The existing ingestion implementation uses deterministic
        # IDs + upsert, so repeated ingestion remains idempotent.
        result = ingest("data/docs")

        return {
            "message": "Document uploaded and indexed successfully.",
            "filename": safe_name,
            "files": result["files"],
            "chunks_upserted": result["chunks_upserted"],
            "total_vectors": result["total_vectors"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ---------------------------------------------------------
# Manual ingestion endpoint
# ---------------------------------------------------------

@app.post("/ingest")
def ingest_api(req: IngestRequest):
    try:
        return ingest(
            req.folder,
            req.chunk_size,
            req.overlap
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ---------------------------------------------------------
# Retrieval-only endpoint
# ---------------------------------------------------------

@app.post("/retrieve")
def retrieve_api(req: QueryRequest):
    try:
        return {
            "question": req.question,
            "k": req.k,
            "contexts": retrieve(
                req.question,
                req.k,
                req.source
            )
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------------------------------------------------
# Full RAG query endpoint
# ---------------------------------------------------------

@app.post("/query")
def query_api(req: QueryRequest):
    try:
        return answer(
            req.question,
            req.k,
            req.source
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )