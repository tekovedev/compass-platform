from compass.pipeline.embedder import get_embeddings
from compass.pipeline.store import VectorStore


def retrieve(query: str, store: VectorStore, top_k: int = 5) -> list[str]:
    """Embed a query and return the top-k most relevant chunks."""
    query_embedding = get_embeddings([query])[0]
    return store.query(query_embedding, top_k=top_k)
