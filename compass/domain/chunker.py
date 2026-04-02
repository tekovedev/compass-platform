def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into fixed-size chunks with overlap."""
    if size <= 0:
        raise ValueError("size must be positive")
    if overlap < 0:
        raise ValueError("overlap must be non-negative")
    if overlap >= size:
        raise ValueError("overlap must be less than size")

    chunks: list[str] = []
    start = 0
    step = size - overlap
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        # If this chunk is entirely within the previous one, skip it
        if chunks and start + len(chunk) <= start - step + size:
            break
        chunks.append(chunk)
        start += step
    return chunks
