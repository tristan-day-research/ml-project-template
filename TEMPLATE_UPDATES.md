# Template Update Policy

This template owns and may overwrite on `copier update` (subject to your conflict resolution):

- `pyproject.toml` structure (dependency pins/versions are project-owned)
- `.github/workflows/*`
- `prefect.yaml`
- Files under `docs/*`
- Files under `configs/*` (excluding any untracked local secrets)
- `scripts/cli.py`

Project-owned (the template will not overwrite without an explicit accept/diff):

- Everything under `src/` (application code and modules)
- Any additional files you add not originally provided by the template

## How to Update

```bash
git switch -c chore/template-update
copier update
# review prompts/diffs
pytest -q
```

## Notes

- The template pins `mlcore` with an upper bound by default (`>=0.1,<0.2`) and supports a local path override (`MLCORE_LOCAL_PATH`) when generating or developing. Update your project’s dependency pins as needed.
