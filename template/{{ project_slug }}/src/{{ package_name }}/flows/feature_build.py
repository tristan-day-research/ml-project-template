from __future__ import annotations

try:
    from prefect import flow, task  # type: ignore
except Exception:  # pragma: no cover
    def flow(fn):  # type: ignore
        return fn

    def task(fn):  # type: ignore
        return fn


@task
def build_features() -> int:
    # TODO: implement feature building
    return 1


@flow(name="feature-build")
def feature_build_flow() -> int:
    return build_features()


if __name__ == "__main__":
    print(feature_build_flow())

