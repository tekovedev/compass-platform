from dataclasses import dataclass
from pathlib import Path


@dataclass
class Document:
    content: str
    source: str


def load_documents(path: str) -> list[Document]:
    """Load .txt and .md files from a directory."""
    dir_path = Path(path)
    documents: list[Document] = []
    for ext in ("*.txt", "*.md"):
        for file in sorted(dir_path.rglob(ext)):
            text = file.read_text(encoding="utf-8")
            documents.append(Document(content=text, source=str(file)))
    return documents
