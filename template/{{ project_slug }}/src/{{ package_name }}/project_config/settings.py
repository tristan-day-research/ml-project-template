from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


class PathsSettings(BaseModel):
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[3]
    )
    data_root: Path = Path("data")
    config_root: Path = Path("app_config")
    cache_root: Path = Path(".cache")

    @model_validator(mode="after")
    def _absolutize(self) -> "PathsSettings":
        pr = self.project_root
        if not self.data_root.is_absolute():
            self.data_root = pr / self.data_root
        if not self.cache_root.is_absolute():
            self.cache_root = pr / self.cache_root
        if not self.config_root.is_absolute():
            self.config_root = pr / self.config_root
        return self


class DataSettings(BaseModel):
    num_workers: int = 4
    chunk_tokens: int = 512
    batch_size: int = 1000
    min_rows: int = 10
    max_missing: float = 0.05


class ModelSettings(BaseModel):
    model_name: str = "baseline_xgb"
    artefact_bucket: str | None = None


class LoggingSettings(BaseModel):
    level: str = "INFO"
    json: bool = False


class PrefectSettings(BaseModel):
    work_pool: str | None = None
    work_queue: str | None = None
    deployment_name: str | None = None


class StateMachineSettings(BaseModel):
    strict_validation: bool = True
    schema_version: str = "v1"


class ProjectSettings(BaseSettings):
    environment: str = "dev"
    debug: bool = False

    paths: PathsSettings = PathsSettings()
    data: DataSettings = DataSettings()
    model: ModelSettings = ModelSettings()
    logging: LoggingSettings = LoggingSettings()
    prefect: PrefectSettings = PrefectSettings()
    state_machine: StateMachineSettings = StateMachineSettings()

    model_config = SettingsConfigDict(
        env_prefix="PRJ_",
        env_nested_delimiter="__",
        env_file=(),  # set below after constants are defined
        env_file_encoding="utf-8",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,  # type: ignore[no-redef]
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        # Precedence: init kwargs > env > .env > YAML > file secrets
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            yaml_settings_source,
            file_secret_settings,
        )


@lru_cache
def get_settings() -> ProjectSettings:
    return ProjectSettings()


# ------------------------- YAML hydration helpers ------------------------- #

DEFAULT_PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_ROOT = DEFAULT_PROJECT_ROOT / "app_config"

# Discover env files once at import time (simple, robust)
ENV_FILES = tuple(
    str(p) for p in [DEFAULT_PROJECT_ROOT / ".env"] if p.exists()
)

# Inject discovered env files into model_config (must be a tuple of paths/strings)
ProjectSettings.model_config["env_file"] = ENV_FILES


def yaml_settings_source() -> Dict[str, Any]:
    """Load overrides from app_config YAMLs.

    Files (if present):
      - app_config/env/{env}.yaml where env = PRJ_ENVIRONMENT | ENVIRONMENT | dev
      - app_config/policies/thresholds.yaml

    YAML keys are mapped into ProjectSettings' nested structure. Environment
    variables still override these values due to source precedence.
    """

    env = os.getenv("PRJ_ENVIRONMENT") or os.getenv("ENVIRONMENT") or "dev"
    cfg_root = DEFAULT_CONFIG_ROOT

    overrides: Dict[str, Any] = {}

    # env-level file
    env_file = cfg_root / "env" / f"{env}.yaml"
    overrides = _merge_dicts(overrides, _map_env_yaml(_read_yaml(env_file)))

    # thresholds/policies
    thresholds_file = cfg_root / "policies" / "thresholds.yaml"
    overrides = _merge_dicts(overrides, _map_thresholds_yaml(_read_yaml(thresholds_file)))

    return overrides


def _read_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            return {}
        return data
    except Exception:
        return {}


def _merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _merge_dicts(out[k], v)
        else:
            out[k] = v
    return out


def _map_env_yaml(d: Dict[str, Any]) -> Dict[str, Any]:
    """Map env YAML structure into ProjectSettings fields.

    Supported keys:
      environment -> environment
      logging.level -> logging.level
      data.root -> paths.data_root
      pipeline.num_workers -> data.num_workers
      pipeline.chunk_tokens -> data.chunk_tokens
    """

    out: Dict[str, Any] = {}
    if not d:
        return out

    if "environment" in d:
        out["environment"] = d["environment"]

    logging = d.get("logging") or {}
    if isinstance(logging, dict) and "level" in logging:
        out.setdefault("logging", {})
        out["logging"]["level"] = logging["level"]

    data = d.get("data") or {}
    if isinstance(data, dict) and "root" in data:
        out.setdefault("paths", {})
        out["paths"]["data_root"] = data["root"]

    pipeline = d.get("pipeline") or {}
    if isinstance(pipeline, dict):
        if "num_workers" in pipeline:
            out.setdefault("data", {})
            out["data"]["num_workers"] = pipeline["num_workers"]
        if "chunk_tokens" in pipeline:
            out.setdefault("data", {})
            out["data"]["chunk_tokens"] = pipeline["chunk_tokens"]

    return out


def _map_thresholds_yaml(d: Dict[str, Any]) -> Dict[str, Any]:
    """Map thresholds YAML into ProjectSettings fields.

    Supported keys:
      validation.min_rows -> data.min_rows
      validation.max_missing -> data.max_missing
      rag.chunk_tokens -> data.chunk_tokens (if not set elsewhere)
    """

    out: Dict[str, Any] = {}
    if not d:
        return out

    validation = d.get("validation") or {}
    if isinstance(validation, dict):
        if "min_rows" in validation:
            out.setdefault("data", {})
            out["data"]["min_rows"] = validation["min_rows"]
        if "max_missing" in validation:
            out.setdefault("data", {})
            out["data"]["max_missing"] = validation["max_missing"]

    rag = d.get("rag") or {}
    if isinstance(rag, dict) and "chunk_tokens" in rag:
        out.setdefault("data", {})
        out["data"].setdefault("chunk_tokens", rag["chunk_tokens"])  # don't override if already set

    return out
