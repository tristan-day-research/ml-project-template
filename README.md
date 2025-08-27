# ml-project-template (Copier)

This is a Copier template for bootstrapping machine-learning projects that follow a data-centric state machine with Prefect v2 orchestration. It renders a clean scaffold with typed config (pydantic-settings), optional Pandera, and a CLI plus minimal Prefect flows. The template is designed to be updatable later via `copier update` without clobbering your project-owned code.

## Use

- Prereqs: Python 3.11+, `pipx install copier` (or `pip install copier`).
- Create a new project:

  ```bash
  copier copy gh:your-org/ml-project-template path/to/your_project
  # or from a local checkout
  copier copy . path/to/your_project
  ```

- Questions include project name, package name, Python version, and whether to enable Prefect/Pandera.

- ml-core dependency:
  - By default, projects depend on `ml-core[prefect] >=0.1,<0.2`.
  - To dogfood locally during generation, set `MLCORE_LOCAL_PATH` env var before running Copier. The generated project will use the local path via uv sources.

## Develop

- Lint/type-check this template repo:

  ```bash
  pre-commit run --all-files
  ```

## Rendered Project

The template renders this structure (verbatim):

```
your_project_name/
├── pyproject.toml
├── prefect.yaml
├── README.md
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── QUICKSTART.md
│
├── configs/
│   ├── env/
│   │   ├── dev.yaml
│   │   └── prod.yaml
│   ├── data_sources.yaml
│   └── policies/
│       └── thresholds.yaml
│
├── registries/
│   ├── schemas/
│   ├── features/
│   └── prompts/
│
├── src/<your_package_name>/
│   ├── tasks/
│   │   ├── io/
│   │   ├── validation/
│   │   ├── featurization/
│   │   ├── modeling/
│   │   └── evaluation/
│   │
│   └── flows/
│       ├── ingest_validate.py
│       ├── feature_build.py
│       ├── train_eval.py
│       └── deploy.py
│
├── lab/
│   ├── notebooks/
│   ├── playbooks/
│   └── overrides/
│
├── scripts/
│   └── cli.py
│
├── tests/
│   ├── unit/
│   └── integration/
│
└── data/
    ├── samples/
    └── fixtures/
```

## Update (copier update)

Projects can be updated later. Run:

```bash
git switch -c chore/template-update
copier update
# review diffs/prompts
pytest -q
```

See `TEMPLATE_UPDATES.md` for the policy on which files are template-owned vs project-owned.

## Two-plane model

- Template plane: this repo defines structure, configs, CI, and example flows/CLI.
- Library plane: `ml-core` contains reusable utilities and abstractions (logging, IO, model cards, etc.). The template pins an upper bound by default to prevent silent breaking changes, and supports a local path override via `MLCORE_LOCAL_PATH` when generating or developing.

## CI

The CI lints this repository and test-generates a sample project using Copier, installs it (pointing `ml-core` to a local stub in this repo), and runs its tests. This ensures the template stays healthy.

