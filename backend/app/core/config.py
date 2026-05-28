from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "info"

    database_url: str = "postgresql+asyncpg://marine:marine@localhost:5432/marine_traffic"
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 60

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    digitraffic_base_url: str = "https://meri.digitraffic.fi"
    digitraffic_timeout_seconds: int = 10
    digitraffic_retry_attempts: int = 3

    risk_weight_vessel_density: int = 25
    risk_weight_port_congestion: int = 20
    risk_weight_sea_state: int = 25
    risk_weight_aton_faults: int = 15
    risk_weight_winter_navigation: int = 15


settings = Settings()
