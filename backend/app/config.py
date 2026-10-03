"""
Central config. Every setting the app needs comes from here, and everywhere
else in the codebase reads settings from this module instead of calling
os.environ directly. This is what makes the SQLite <-> Postgres swap a
one-line change later: nothing else needs to know or care.
"""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    groq_api_key: str
    env: str

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith("postgresql")


def get_settings() -> Settings:
    return Settings(
        database_url=os.environ.get("DATABASE_URL", "sqlite:///./titan.db"),
        groq_api_key=os.environ.get("GROQ_API_KEY", ""),
        env=os.environ.get("APP_ENV", "development"),
    )


settings = get_settings()