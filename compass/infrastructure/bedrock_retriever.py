import boto3

from compass.config import settings


def retrieve(query: str, top_k: int = 5) -> list[str]:
    """Retrieve relevant chunks from the AWS Bedrock Knowledge Base."""
    client = boto3.client("bedrock-agent-runtime", region_name=settings.aws_region)

    response = client.retrieve(
        knowledgeBaseId=settings.knowledge_base_id,
        retrievalQuery={"text": query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {"numberOfResults": top_k}
        },
    )

    return [
        result["content"]["text"]
        for result in response["retrievalResults"]
    ]
