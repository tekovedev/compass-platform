from __future__ import annotations

import json

import boto3

from compass.config import settings


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Get embeddings for a list of texts via Amazon Bedrock Titan."""
    client = boto3.client("bedrock-runtime", region_name=settings.aws_region)
    embeddings: list[list[float]] = []
    for text in texts:
        response = client.invoke_model(
            modelId=settings.embedding_model_id,
            body=json.dumps({"inputText": text}),
        )
        result = json.loads(response["body"].read())
        embeddings.append(result["embedding"])
    return embeddings
