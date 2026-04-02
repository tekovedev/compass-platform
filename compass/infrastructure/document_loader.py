from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests


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


def load_from_url(url: str, output_dir: str = "data") -> list[dict]:
    """Fetch a webpage, split it by HTML sections, and write a JSONL file."""
    from compass.infrastructure.html_splitter import split_html

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = Path(urlparse(url).path).stem or "page"
    output_path = out_dir / f"{filename}.jsonl"

    return split_html(response.text, str(output_path))


if __name__ == "__main__":
    import sys

    url = sys.argv[1]
    sections = load_from_url(url)
    print(f"{len(sections)} sections written")
