from __future__ import annotations

import asyncio

from compass.config import settings
from compass.domain.chunker import chunk_text
from compass.infrastructure.document_loader import load_documents
from compass.infrastructure.bedrock_embedder import get_embeddings
from compass.infrastructure.vector_store import VectorStore

_store: VectorStore | None = None


def _get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore(
            endpoint=settings.opensearch_endpoint,
            index_name=settings.opensearch_index,
        )
    return _store


class IngestService:
    async def execute(self, path: str) -> int:
        """Load documents, chunk, embed, and store. Returns chunks_stored."""
        documents = await asyncio.to_thread(load_documents, path)
        all_chunks: list[str] = []
        for doc in documents:
            chunks = chunk_text(doc.content, settings.chunk_size, settings.chunk_overlap)
            all_chunks.extend(chunks)

        embeddings = await asyncio.to_thread(get_embeddings, all_chunks)
        store = await asyncio.to_thread(_get_store)
        await asyncio.to_thread(store.add, all_chunks, embeddings)
        return len(all_chunks)
