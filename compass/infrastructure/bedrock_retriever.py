import logging

import boto3

from compass.config import settings

logger = logging.getLogger(__name__)

_RRF_K = 60


def reciprocal_rank_fusion(ranked_lists: list[list[str]], k: int = _RRF_K) -> list[str]:
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, chunk in enumerate(ranked):
            scores[chunk] = scores.get(chunk, 0.0) + 1.0 / (rank + k)
    return sorted(scores, key=lambda c: scores[c], reverse=True)


def retrieve(queries: list[str], top_k: int = 5) -> list[str]:
    """Retrieve relevant chunks from the AWS Bedrock Knowledge Base.

    Calls the knowledge base once per query and returns a deduplicated
    list of text chunks.
    """
    client = boto3.client("bedrock-agent-runtime", region_name=settings.aws_region)
    ranked_lists: list[list[str]] = []

    for query in queries:
        response = client.retrieve(
            knowledgeBaseId=settings.knowledge_base_id,
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "vectorSearchConfiguration": {"numberOfResults": top_k}
            },
        )

        query_chunks = [r["content"]["text"] for r in response["retrievalResults"]]
        logger.info("query=%r chunks=%s", query, query_chunks)
        ranked_lists.append(query_chunks)

    return reciprocal_rank_fusion(ranked_lists)
