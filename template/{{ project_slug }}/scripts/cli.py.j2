from __future__ import annotations

import argparse
import importlib
import sys


def run_train_eval() -> None:
    mod = importlib.import_module("{{ package_name }}.flows.train_eval")
    res = mod.train_eval_flow()  # type: ignore[attr-defined]
    print(res)


def run_ingest_validate() -> None:
    mod = importlib.import_module("{{ package_name }}.flows.ingest_validate")
    res = mod.ingest_validate_flow()  # type: ignore[attr-defined]
    print(res)


def run_feature_build() -> None:
    mod = importlib.import_module("{{ package_name }}.flows.feature_build")
    res = mod.feature_build_flow()  # type: ignore[attr-defined]
    print(res)


def run_deploy() -> None:
    mod = importlib.import_module("{{ package_name }}.flows.deploy")
    res = mod.deploy_flow()  # type: ignore[attr-defined]
    print(res)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ml-cli")
    sub = parser.add_subparsers(dest="cmd")

    run = sub.add_parser("run", help="Run a flow")
    run.add_argument(
        "flow",
        choices=["train-eval", "ingest-validate", "feature-build", "deploy"],
    )

    args = parser.parse_args(argv)
    if args.cmd == "run":
        if args.flow == "train-eval":
            run_train_eval()
        elif args.flow == "ingest-validate":
            run_ingest_validate()
        elif args.flow == "feature-build":
            run_feature_build()
        elif args.flow == "deploy":
            run_deploy()
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

