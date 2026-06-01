from __future__ import annotations

import re

_ARTICLE_PATTERN = re.compile(r"Artículo\s+\d+[°º]?\.-", re.UNICODE)


def extract_articles(chunks: list[str]) -> list[str]:
    """Split raw retrieval chunks into individual article strings.

    Each article runs from its header up to (but not including) the next one.
    Duplicate articles across chunks are dropped; original order is preserved.
    """
    articles: list[str] = []
    seen: set[str] = set()

    for chunk in chunks:
        # Find positions of every article header in this chunk
        matches = list(_ARTICLE_PATTERN.finditer(chunk))
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(chunk)
            article = chunk[start:end].strip()
            if article and article not in seen:
                seen.add(article)
                articles.append(article)
    print(f"ARticles { articles} ")

    return articles
