from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Các key cũ (Giữ nguyên)
    google_api_key: str
    qdrant_cloud_url: str
    qdrant_api_key: str
    qdrant_collection: str = "notebooklm_docs"

    # --- THÊM 2 DÒNG NÀY ---
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    # -----------------------

    gemini_model: str = "gemini-2.0-flash"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()