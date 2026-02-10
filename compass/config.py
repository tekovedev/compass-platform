from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    aws_region: str = "us-east-1"
    opensearch_endpoint: str = ""
    opensearch_index: str = "documents"
    embedding_model_id: str = "amazon.titan-embed-text-v2:0"
    llm_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"
    chunk_size: int = 500
    chunk_overlap: int = 50

    model_config = {"env_file": ".env"}


settings = Settings()
