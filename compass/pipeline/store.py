from __future__ import annotations

import uuid

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


class VectorStore:
    """Thin wrapper around an OpenSearch Serverless collection."""

    def __init__(self, endpoint: str, index_name: str = "documents") -> None:
        credentials = boto3.Session().get_credentials()
        aws_auth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            boto3.Session().region_name or "us-east-1",
            "aoss",
            session_token=credentials.token,
        )

        self._index = index_name
        self._client = OpenSearch(
            hosts=[{"host": endpoint, "port": 443}],
            http_auth=aws_auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
        )
        self._ensure_index()

    def _ensure_index(self) -> None:
        if not self._client.indices.exists(self._index):
            self._client.indices.create(
                self._index,
                body={
                    "settings": {"index": {"knn": True}},
                    "mappings": {
                        "properties": {
                            "text": {"type": "text"},
                            "embedding": {
                                "type": "knn_vector",
                                "dimension": 1024,
                                "method": {
                                    "name": "hnsw",
                                    "space_type": "l2",
                                    "engine": "faiss",
                                },
                            },
                        }
                    },
                },
            )

    def add(self, texts: list[str], embeddings: list[list[float]]) -> None:
        for text, emb in zip(texts, embeddings):
            self._client.index(
                index=self._index,
                id=uuid.uuid4().hex,
                body={"text": text, "embedding": emb},
            )
        self._client.indices.refresh(index=self._index)

    def query(self, embedding: list[float], top_k: int = 5) -> list[str]:
        body = {
            "size": top_k,
            "query": {"knn": {"embedding": {"vector": embedding, "k": top_k}}},
        }
        results = self._client.search(index=self._index, body=body)
        return [hit["_source"]["text"] for hit in results["hits"]["hits"]]
