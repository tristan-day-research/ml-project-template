from __future__ import annotations

from ..project_config import get_settings  # project settings entrypoint

# Deploy

try:
    from prefect import flow  # type: ignore
except Exception:  # pragma: no cover
    def flow(fn):  # type: ignore
        return fn



@flow(name="deploy")
def deploy_flow() -> str:
    # TODO: implement deployment routine
    return "deployed"


if __name__ == "__main__":
    print(deploy_flow())
