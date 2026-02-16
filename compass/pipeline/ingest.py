"""Ingest pipeline: read JSONL sections, embed with Titan, load into OpenSearch."""

import json
import sys
from pathlib import Path

from compass.config import settings
from compass.pipeline.embedder import get_embeddings
from compass.pipeline.store import VectorStore


def ingest(jsonl_path: str, batch_size: int = 10) -> None:
    """Read a JSONL file and index each section into OpenSearch."""
    sections = []
    with Path(jsonl_path).open(encoding="utf-8") as f:
        for line in f:
            sections.append(json.loads(line))

    store = VectorStore(settings.opensearch_endpoint, settings.opensearch_index)

    for i in range(0, len(sections), batch_size):
        batch = sections[i : i + batch_size]
        texts = [s["content"] for s in batch]
        embeddings = get_embeddings(texts)
        store.add(texts, embeddings)
        print(f"Indexed {min(i + batch_size, len(sections))}/{len(sections)}")

    print("Done")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/BO-COD-DL10135.jsonl"
    ingest(path)
