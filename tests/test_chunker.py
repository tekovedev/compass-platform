import pytest

from compass.pipeline.chunker import chunk_text


def test_single_chunk():
    text = "hello"
    chunks = chunk_text(text, size=10, overlap=2)
    assert chunks == ["hello"]


def test_exact_size():
    text = "abcde"
    chunks = chunk_text(text, size=5, overlap=0)
    assert chunks == ["abcde"]


def test_overlap():
    text = "abcdefghij"
    chunks = chunk_text(text, size=5, overlap=2)
    assert chunks == ["abcde", "defgh", "ghij"]


def test_no_overlap():
    text = "abcdefghij"
    chunks = chunk_text(text, size=5, overlap=0)
    assert chunks == ["abcde", "fghij"]


def test_empty_text():
    assert chunk_text("", size=5, overlap=0) == []


def test_invalid_size():
    with pytest.raises(ValueError, match="size must be positive"):
        chunk_text("hello", size=0, overlap=0)


def test_overlap_exceeds_size():
    with pytest.raises(ValueError, match="overlap must be less than size"):
        chunk_text("hello", size=5, overlap=5)
