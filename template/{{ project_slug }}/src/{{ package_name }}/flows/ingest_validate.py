from __future__ import annotations

from typing import Any, Dict

try:
    from prefect import flow, task  # type: ignore
except Exception:  # pragma: no cover
    def flow(fn):  # type: ignore
        return fn

    def task(fn):  # type: ignore
        return fn


@task
def ingest() -> Dict[str, Any]:
    # TODO: implement ingestion
    return {"rows": 10}


@task
def validate(payload: Dict[str, Any]) -> bool:
    # TODO: implement validations (pydantic, optional pandera)
    return bool(payload)


@flow(name="ingest-validate")
def ingest_validate_flow() -> bool:
    data = ingest()
    return validate(data)


if __name__ == "__main__":
    print(ingest_validate_flow())

