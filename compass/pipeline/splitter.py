import json
import re
from pathlib import Path

from langchain_text_splitters import HTMLSectionSplitter


HEADERS_TO_SPLIT_ON = [
    ("h1", "Header 1"),
    ("h2", "Header 2"),
    ("h3", "Header 3"),
]


def split_html(html: str, output_path: str = "data/sections.jsonl") -> list[dict]:
    """Split HTML by sections and write each section as a JSONL row."""
    # Strip XML/HTML encoding declarations so lxml can parse the string
    html = re.sub(r'<\?xml[^?]*\?>', '', html)
    html = re.sub(r'charset=["\']?[^"\'\s>]+["\']?', '', html, flags=re.IGNORECASE)

    splitter = HTMLSectionSplitter(HEADERS_TO_SPLIT_ON)
    docs = splitter.split_text(html)

    sections = [
        {"content": doc.page_content, "metadata": doc.metadata}
        for doc in docs
    ]

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for section in sections:
            f.write(json.dumps(section, ensure_ascii=False) + "\n")

    return sections
