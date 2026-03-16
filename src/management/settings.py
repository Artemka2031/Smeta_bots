from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


class ProjectDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    project_key: str
    name: str
    token: str
    url: str
    enabled: bool = True
    work_chat: str | None = None
    bot_link: str | None = None


class RuntimeProject(ProjectDefinition):
    def to_runtime_dict(self) -> dict[str, object]:
        return {
            "project_key": self.project_key,
            "name": self.name,
            "token": self.token,
            "url": self.url,
            "work_chat": self.work_chat,
            "bot_link": self.bot_link,
        }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    base_dir: Path = Field(default_factory=_project_root)
    projects_config_path: Path = Field(default_factory=lambda: _project_root() / "src" / "management" / "projects.yaml")
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="smeta_bots")
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="postgres")
    google_service_account_json: str | None = Field(default=None)
    google_service_account_type: str = Field(default="service_account")
    google_project_id: str | None = Field(default=None)
    google_private_key_id: str | None = Field(default=None)
    google_private_key: str | None = Field(default=None)
    google_client_email: str | None = Field(default=None)
    google_client_id: str | None = Field(default=None)
    google_auth_uri: str = Field(default="https://accounts.google.com/o/oauth2/auth")
    google_token_uri: str = Field(default="https://oauth2.googleapis.com/token")
    google_auth_provider_x509_cert_url: str = Field(
        default="https://www.googleapis.com/oauth2/v1/certs"
    )
    google_client_x509_cert_url: str | None = Field(default=None)
    google_universe_domain: str = Field(default="googleapis.com")
    sqlalchemy_echo: bool = False

    def load_project_catalog(self) -> list[ProjectDefinition]:
        with self.projects_config_path.open("r", encoding="utf-8") as file:
            payload = yaml.safe_load(file) or {}

        raw_projects = payload.get("projects", [])
        return [ProjectDefinition.model_validate(project) for project in raw_projects]

    def load_runtime_projects(self) -> list[RuntimeProject]:
        return [RuntimeProject.model_validate(project.model_dump(by_alias=True)) for project in self.load_project_catalog()]

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def alembic_database_url(self) -> str:
        return ( 
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    @property
    def google_credentials_payload(self) -> str:
        if self.google_service_account_json:
            return self.google_service_account_json

        required_values = {
            "project_id": self.google_project_id,
            "private_key_id": self.google_private_key_id,
            "private_key": self.google_private_key,
            "client_email": self.google_client_email,
            "client_id": self.google_client_id,
            "client_x509_cert_url": self.google_client_x509_cert_url,
        }
        missing_fields = [field_name for field_name, value in required_values.items() if not value]
        if missing_fields:
            missing_envs = ", ".join(f"GOOGLE_{field_name.upper()}" for field_name in missing_fields)
            raise ValueError(f"Missing Google service account env vars: {missing_envs}")

        payload = {
            "type": self.google_service_account_type,
            "project_id": self.google_project_id,
            "private_key_id": self.google_private_key_id,
            "private_key": self.google_private_key.replace("\\n", "\n"),
            "client_email": self.google_client_email,
            "client_id": self.google_client_id,
            "auth_uri": self.google_auth_uri,
            "token_uri": self.google_token_uri,
            "auth_provider_x509_cert_url": self.google_auth_provider_x509_cert_url,
            "client_x509_cert_url": self.google_client_x509_cert_url,
            "universe_domain": self.google_universe_domain,
        }
        return json.dumps(payload)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
