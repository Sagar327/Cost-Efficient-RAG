from pathlib import Path
import chromadb

class ChromaStore:
    def __init__(self, path: str, collection_name: str, embedding_model):
        Path(path).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Cost-efficient RAG chunk store"}
        )
        self.embedding_model = embedding_model

    def upsert(self, chunks):
        if not chunks:
            return
        texts = [c.text for c in chunks]
        vectors = self.embedding_model.encode(texts, normalize_embeddings=True).tolist()
        self.collection.upsert(
            ids=[c.id for c in chunks],
            embeddings=vectors,
            documents=texts,
            metadatas=[{
                "source": c.source,
                "chunk_index": c.chunk_index,
                "start_char": c.start_char,
                "end_char": c.end_char,
            } for c in chunks],
        )

    def query(self, query: str, k: int = 5, source: str | None = None):
        q = self.embedding_model.encode([query], normalize_embeddings=True).tolist()
        kwargs = dict(query_embeddings=q, n_results=k, include=["documents", "metadatas", "distances"])
        if source:
            kwargs["where"] = {"source": source}
        return self.collection.query(**kwargs)

    def count(self):
        return self.collection.count()
