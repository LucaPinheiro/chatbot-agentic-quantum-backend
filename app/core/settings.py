# app/core/settings.py

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum


class StageEnum(str, Enum):
    prod = "prod"
    dev = "dev"
    test = "test"
    local = "local"


SUFFIXES = {
    StageEnum.dev: "_dev",
    StageEnum.prod: "_prod",
    StageEnum.test: "_test",
    StageEnum.local: "",
}


class Settings(BaseSettings):
    # ─────────────── App Metadata ───────────────
    project_name: str = "Quantum Tutor Chatbot API"
    description: str = "Chatbot tutor de computação quântica com RAG e multi‑agentes"
    version: str = "0.1.0"
    api_v1_str: str = "/api/v1"

    # ─────────────── Runtime ───────────────
    stage: StageEnum = StageEnum.local
    debug: bool = False
    log_level: str = "INFO"

    # ─────────────── CORS / Segurança ───────────────
    backend_cors_origins: str = ""
    jwt_secret: str = "JWT_SECRET"  
    secret_key: str = "SECRET_KEY"
    access_token_expire_minutes: int = 30

    # ─────────────── Database / Cache ───────────────
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "quantum_chat"

    redis_host: str = "redis"
    redis_port: int = 6379
    
    # --------------- SQS QUEUES ---------------
    sqs_queue_url: str = ""  

    # ─────────────── Overrides (opcional) ───────────────
    postgres_url_prefix: str | None = None
    redis_url_prefix: str | None = None
    s3_bucket_prefix: str = "qt-chatbot"

    # ─────────────── AWS / DynamoDB ───────────────
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    aws_s3_bucket: str = "qt-chatbot"
    dynamodb_region: str = "sa-east-1"
    dynamodb_table_messages: str = ""

    # ─────────────── LLM / RAG / Embeddings ───────────────
    openai_api_key: str = ""
    
    # use_bedrock: bool = False
    # use_local_model: bool = True
    # bedrock_model_id: str = ""
    # bedrock_region: str = ""
    # bedrock_role_arn: str = ""
    # embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    # vector_index_path: str = "./vectorstore"

    # ─────────────── Computed Properties ───────────────
    @property
    def postgres_url(self) -> str:
        suffix = SUFFIXES[self.stage]
        if self.postgres_url_prefix:
            return self.postgres_url_prefix + suffix
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}{suffix}"
        )
        
    @property
    def redis_url(self) -> str:
        suffix = SUFFIXES[self.stage]
        if self.redis_url_prefix:
            return self.redis_url_prefix + suffix
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @property
    def s3_bucket(self) -> str:
        return self.s3_bucket_prefix + SUFFIXES[self.stage]

    # ─────────────── Configuração do Pydantic ───────────────
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="forbid"
    )


@lru_cache
def load_settings() -> Settings:
    return Settings()
