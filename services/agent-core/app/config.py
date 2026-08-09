from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AEGIS"
    environment: str = "development"
    openai_api_key: str = ""
    openai_model: str = "gpt-5-nano"
    embedding_model: str = "text-embedding-3-small"
    max_agent_turns: int = 12
    memory_db_path: str = "./data/aegis.db"


settings = Settings()
