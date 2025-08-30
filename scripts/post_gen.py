#!/usr/bin/env python
"""Post-generation hook.

Print next steps, optionally install pre-commit, and handle conditional dependencies.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import toml
from pathlib import Path
import re


def update_pyproject_with_conditional_deps():
    """Update pyproject.toml after generation.

    - Add conditional dependencies (prefect/pandera) based on Copier answers.
    - If environment variable MLCORE_LOCAL_PATH is set, add a local
      uv source for mlcore: `[tool.uv.sources] mlcore = { path = ..., editable = true }`.
    """
    try:
        project_dir = Path.cwd()
        pyproject_path = project_dir / "pyproject.toml"
        
        # Read the current pyproject.toml
        with open(pyproject_path, 'r') as f:
            data = toml.load(f)
        
        # Get Copier answers to check user choices
        answers_path = project_dir / ".copier-answers.yml"
        if answers_path.exists():
            # Simple parsing of copier answers (you could use pyyaml for better parsing)
            with open(answers_path, 'r') as f:
                answers_content = f.read()
            
            # Check user choices from answers
            use_prefect = 'use_prefect: true' in answers_content.lower()
            use_pandera = 'use_pandera: true' in answers_content.lower()
            
            # Get dependencies list
            if 'project' in data and 'dependencies' in data['project']:
                dependencies = data['project']['dependencies']
                
                # Add prefect if requested
                if use_prefect and "prefect>=2.16.0" not in str(dependencies):
                    dependencies.append("prefect>=2.16.0")
                
                # Add pandera if requested  
                if use_pandera and "pandera>=0.18.0" not in str(dependencies):
                    dependencies.append("pandera>=0.18.0")
                
                # Update the dependencies
                data['project']['dependencies'] = dependencies
                
        # Optionally wire local mlcore for both uv and pip
        mlcore_local = os.getenv("MLCORE_LOCAL_PATH")
        if mlcore_local:
            # uv: add local source mapping (used by `uv sync`)
            tool = data.setdefault("tool", {})
            uv = tool.setdefault("uv", {})
            sources = uv.setdefault("sources", {})
            sources["mlcore"] = {"path": mlcore_local, "editable": True}

            # pip: replace any 'mlcore...' dependency with a direct path reference
            try:
                abs_path = Path(mlcore_local)
                if not abs_path.is_absolute():
                    abs_path = (project_dir / abs_path).resolve()
                file_ref = f"file://{abs_path}"

                deps = data.get("project", {}).get("dependencies", [])
                new_deps: list[str] = []
                pattern = re.compile(r"^\s*mlcore(\[[^\]]+\])?(\s*.*)?$")
                replaced = False
                for dep in deps:
                    if isinstance(dep, str):
                        m = pattern.match(dep)
                        if m:
                            extras = m.group(1) or ""
                            new_deps.append(f"mlcore{extras} @ {file_ref}")
                            replaced = True
                            continue
                    new_deps.append(dep)
                if replaced:
                    data.setdefault("project", {})["dependencies"] = new_deps
                else:
                    # If no existing mlcore dep, append a direct path reference
                    new_deps.append(f"mlcore @ {file_ref}")
                    data.setdefault("project", {})["dependencies"] = new_deps
            except Exception as exc:  # noqa: BLE001
                print(f"⚠️  Could not rewrite mlcore dependency for pip: {exc}")

        # Write back the modified pyproject.toml if we changed anything
        with open(pyproject_path, 'w') as f:
            toml.dump(data, f)

        print("✅ Updated pyproject.toml with conditional deps and local sources (if any)")
        
    except Exception as e:
        print(f"⚠️  Could not update pyproject.toml: {e}")
        print("You may need to manually add prefect/pandera dependencies")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true", help="Run pre-commit install")
    args = parser.parse_args(argv)

    # Update pyproject.toml with conditional dependencies
    update_pyproject_with_conditional_deps()

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
