#!/usr/bin/env python
"""Post-generation hook.

Print next steps and optionally install pre-commit.

This script does not install project dependencies by default. Pass --install
to also run `pre-commit install`.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true", help="Run pre-commit install")
    args = parser.parse_args(argv)

    project_dir = os.getcwd()
    msg = f"""
    ✅ Project generated at: {project_dir}

    Next steps:
      1) Create a virtualenv (e.g., `uv venv` or `python -m venv .venv`)
      2) Activate it and install deps (e.g., `uv sync` or `pip install -e .`)
      3) (Optional) Install pre-commit: `pre-commit install`
      4) Run tests: `pytest -q`
      5) Try a flow: `python -m scripts.cli run train-eval`

    Update later with:
      git switch -c chore/template-update && copier update
    """.strip()
    print(msg)

    if args.install:
        try:
            subprocess.check_call([sys.executable, "-m", "pre_commit", "install"])  # type: ignore[attr-defined]
        except Exception as exc:  # noqa: BLE001
            print(f"pre-commit install failed: {exc}")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

