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

- mlcore dependency (optional):
  - Projects may include `mlcore[prefect] >=0.1,<0.2`, but it’s optional.
  - To dogfood locally during generation, set `MLCORE_LOCAL_PATH` env var before running Copier. The generated project will use the local path via uv sources.

### Bootstrap Script (Automation)

Automate the full flow (copy template → create venv → install deps → open shell):

```bash
# From the parent folder that contains ml-project-template/ and (optionally) mlcore/
python ml-project-template/scripts/new_project.py --name my-new-project --use-python311
```

Behavior:
- Creates the project as a sibling of `ml-project-template/` (no nested folder).
- Detects `../mlcore` and installs it editable, or pass `--mlcore-path none` to skip.
- Creates `.venv`, upgrades pip, installs the project editable, and drops you into an activated shell in the new project directory.

Useful flags:
- `--source local|gh`: choose local template or GitHub (default: local)
- `--template-path <path>`: path to local template (auto-detected by default)
- `--parent-dir <dir>`: parent directory holding siblings (auto-detected)
- `--mlcore-path <path|none>`: path to local mlcore or `none` to disable
- `--skip-venv`: only generate the project, no venv or installs
- `--enter/--no-enter`: open an activated subshell in the project (default: enter)
- `--shell <name>`: force shell (e.g., bash, zsh, fish); otherwise detected
- `--clean`: start a shell without user rc files (zsh -f, bash --noprofile --norc)

Copier availability:
- If `copier` isn’t on PATH, the script bootstraps a tiny venv in `ml-project-template/.bootstrap`, installs Copier there, and uses it automatically.

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

## Versioning

- Source of truth for the generated project’s version is `pyproject.toml` under `[project].version`.
- In this template the default is set in:
  - `template/{{ project_slug }}/pyproject.toml.j2:7`
- Recommended initial versioning (Semantic Versioning):
  - Private/prototype: `0.0.1`
  - First usable/internal release: `0.1.0`
  - Public/production baseline: `1.0.0`
- Tag format on GitHub: `vX.Y.Z` (e.g., `v0.1.0`), and ensure the tag points to the commit on your default branch that contains the version bump.

## Two-plane model

- Template plane: this repo defines structure, configs, CI, and example flows/CLI.
- Library plane: `mlcore` contains reusable utilities and abstractions (logging, IO, model cards, etc.). The template pins an upper bound by default to prevent silent breaking changes, and supports a local path override via `MLCORE_LOCAL_PATH` when generating or developing.

## CI

The CI lints this repository and test-generates a sample project using Copier, installs it (pointing `mlcore` to a local stub in this repo), and runs its tests. This ensures the template stays healthy.

### E2E Sanity Locally

- Run `scripts/e2e_sanity.sh` to generate two sample projects:
  - Scenario A: no `mlcore` dependency
  - Scenario B: with local `mlcore` via `MLCORE_LOCAL_PATH`
  It installs, runs tests, and executes the demo flow in both cases.
