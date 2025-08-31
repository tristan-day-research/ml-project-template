from __future__ import annotations

from typing import Any, Dict
from ..project_config import get_settings  # project settings entrypoint

try:
    from prefect import flow, task  # type: ignore
except Exception:  # pragma: no cover - allow running without prefect installed
    def flow(fn):  # type: ignore
        return fn

    def task(fn):  # type: ignore
        return fn

try:
    from mlcore import get_logger, read_json, ModelCard
except Exception:  # fallback stubs if mlcore not installed
    import json
    import logging
    from pathlib import Path

    def get_logger(name: str):  # type: ignore
        return logging.getLogger(name)

    def read_json(p: str):  # type: ignore
        return json.loads(Path(p).read_text())

    class ModelCard(dict):  # type: ignore
        def __init__(self, **kwargs):
            super().__init__(**kwargs)



@task
def load_config(path: str) -> Dict[str, Any]:
    return read_json(path)


@task
def train_model(cfg: Dict[str, Any]) -> Dict[str, float]:
    return {"auc": 0.5}


@task
def log_card(metrics: Dict[str, float]) -> None:
    card = ModelCard(name="demo", version="0.1.0", metrics=metrics)  # type: ignore[arg-type]
    get_logger(__name__).info({"model_card": dict(card)})


@flow(name="train-eval")
def train_eval_flow(config_path: str = "configs/data_sources.yaml") -> Dict[str, float]:
    cfg = load_config(config_path)
    metrics = train_model(cfg)
    log_card(metrics)
    return metrics


if __name__ == "__main__":
    print(train_eval_flow())
