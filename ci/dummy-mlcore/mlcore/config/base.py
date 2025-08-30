from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class CoreBaseSettings(BaseSettings):
    """Base class for project settings shared via mlcore.

    Keeps mlcore stateless while letting projects define concrete settings.
    """

    model_config = SettingsConfigDict(env_file_encoding="utf-8")


def load_env_files(env: str | None) -> list[str]:
    """Return a list of .env files to load for a given environment.

    Example pattern if projects use env-specific files:
    [".env", f"configs/env/{env}.env"]
    """

    return []


def yaml_sources(env: str | None) -> list[str]:
    """Return a list of YAML files that may hydrate settings.

    Example pattern if projects use env-specific YAML config:
    [f"configs/env/{env}.yaml", "configs/data_sources.yaml"]
    """

    return []

