import boto3

from compass.config import settings


def retrieve(queries: list[str], top_k: int = 5) -> list[str]:
    """Retrieve relevant chunks from the AWS Bedrock Knowledge Base.

    Calls the knowledge base once per query and returns a deduplicated
    list of text chunks.
    """
    client = boto3.client("bedrock-agent-runtime", region_name=settings.aws_region)
    seen: set[str] = set()
    chunks: list[str] = []

    for query in queries:
        response = client.retrieve(
            knowledgeBaseId=settings.knowledge_base_id,
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "vectorSearchConfiguration": {"numberOfResults": top_k}
            },
        )

        for result in response["retrievalResults"]:
            text = result["content"]["text"]
            if text not in seen:
                seen.add(text)
                chunks.append(text)

    return chunks
