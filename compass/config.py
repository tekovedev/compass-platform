from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    aws_region: str = "us-east-1"
    opensearch_endpoint: str = ""
    opensearch_index: str = "cod_transito_index"
    embedding_model_id: str = "amazon.titan-embed-text-v2:0"
    llm_model_id: str = "amazon.nova-pro-v1:0"
    query_expansion_model_id: str = "amazon.nova-lite-v1:0"
    knowledge_base_id: str = ""
    agentcore_runtime_arn: str | None = None
    guardrail_id: str | None = None
    guardrail_version: str = "DRAFT"
    cognito_user_pool_id: str | None = None
    cognito_client_id: str | None = None
    cognito_domain: str | None = None
    cognito_region: str | None = None
    chat_sessions_table_name: str | None = None
    chat_conversations_table_name: str | None = None
    chat_monthly_usage_table_name: str | None = None
    monthly_token_limit: int = 200000

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
