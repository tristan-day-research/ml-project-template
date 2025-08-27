# Quickstart

## 1) Create environment and install

```bash
uv venv && source .venv/bin/activate
uv pip install -e .
```

## 2) Try a flow

```bash
python -m scripts.cli run train-eval
```

Open the Prefect UI locally if running a local server (optional). Flows are simple and runnable without external services.

## 3) Switch environments

```bash
export APP_ENV=dev  # or prod
```

## 4) Update later

```bash
git switch -c chore/template-update
copier update
pytest -q
```

