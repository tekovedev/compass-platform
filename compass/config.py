from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    aws_region: str = "us-east-1"
    opensearch_endpoint: str = ""
    opensearch_index: str = "cod_transito_index"
    embedding_model_id: str = "amazon.titan-embed-text-v2:0"
    llm_model_id: str = "amazon.nova-pro-v1:0"
    knowledge_base_id: str = "0ZAUEJ8LFT"
    chunk_size: int = 500
    chunk_overlap: int = 50
    guardrail_id: str | None = None
    guardrail_version: str = "DRAFT"
    cognito_user_pool_id: str | None = None
    cognito_client_id: str | None = None
    cognito_domain: str | None = None
    cognito_region: str | None = None

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
