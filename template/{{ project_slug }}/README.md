# {{ project_name }}

Scaffold generated from the `ml-project-template` (Copier). Includes typed configs, Prefect flows, and a simple CLI. Safe to update later with `copier update`.

## Install

- Using uv (recommended):
  - `uv venv && source .venv/bin/activate`
  - `uv pip install -e .`
- Or pip:
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install -e .`

Notes:
- By default, depends on `ml-core[prefect] >=0.1,<0.2`.
- If you set `MLCORE_LOCAL_PATH` during generation, this project uses that local path via uv sources.

## Run

- Local quick test:
  - `pytest -q`
- Run a flow directly:
  - `python -m scripts.cli run train-eval`
- Environment:
  - Set `APP_ENV=dev` or `APP_ENV=prod` to switch configs (see `configs/env/*`).

## Update

To update the project from the template later:

```bash
git switch -c chore/template-update
copier update
# review diffs, run tests
pytest -q
```

See `TEMPLATE_UPDATES.md` in the template repo for ownership policy.

## Two-plane model

- Template plane (this repo): structure, configs, example flows & CLI.
- Library plane (`ml-core`): reusable utilities (logging, IO, model cards, etc.). This project pins an upper bound by default and supports local development via `MLCORE_LOCAL_PATH`.

