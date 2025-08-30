#!/usr/bin/env python
"""Bootstrap a new project from ml-project-template.

Assumes a parent folder containing siblings:
  - ml-project-template/ (this repo)
  - mlcore/ (optional local library)

Creates a new project as another sibling, sets up a virtualenv, and installs deps.

Usage (from the parent folder with both repos checked out):
  python scripts/new_project.py --name my-new-project

Flexible options let you choose local or GitHub template sources, override paths,
and control how `mlcore` is installed.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
import re


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    print(f"[cmd] {' '.join(cmd)}" + (f"  (cwd={cwd})" if cwd else ""))
    subprocess.check_call(cmd, cwd=str(cwd) if cwd else None, env=env)


def which_python_311() -> str | None:
    """Find a Python 3.11 interpreter path on this system.

    - On Windows, try the py launcher to locate the exact exe.
    - Else, try common names and validate the version.
    """
    try:
        if os.name == "nt":
            # Ask the Windows launcher where 3.11 lives
            out = subprocess.check_output(
                ["py", "-3.11", "-c", "import sys; print(sys.executable)"] ,
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            if out and Path(out).exists():
                return out
    except Exception:
        pass

    candidates = [
        "python3.11",
        "python3",
        "python",
    ]
    for cand in candidates:
        exe = shutil.which(cand)
        if not exe:
            continue
        try:
            ver = subprocess.check_output(
                [exe, "-c", "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            if ver == "3.11":
                return exe
        except Exception:
            continue
    return None


def find_copier_cmd(repo_root: Path) -> list[str]:
    """Find an invocation for Copier that works in this environment.

    Preference order:
      1) `copier` executable on PATH (pipx or pip install)
      2) `python3 -m copier` if available
      3) `python -m copier` if available
      4) Bootstrap local venv under the repo and install copier
    """
    exe = shutil.which("copier")
    if exe:
        return [exe]

    candidates = [
        shutil.which("python3") or "python3",
        shutil.which("python") or "python",
    ]
    for cand in candidates:
        try:
            subprocess.check_call([cand, "-m", "copier", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return [cand, "-m", "copier"]
        except Exception:
            continue

    # Bootstrap: create a minimal venv in the repo to host copier
    bootstrap_dir = repo_root / ".bootstrap"
    venv_dir = bootstrap_dir / "venv"
    python = sys.executable
    try:
        bootstrap_dir.mkdir(parents=True, exist_ok=True)
        # Create venv if missing
        if not (venv_dir / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")).exists():
            subprocess.check_call([python, "-m", "venv", str(venv_dir)])
        vpy, vpip = venv_paths(venv_dir)

        # Prefer uv if available globally; otherwise use pip
        have_uv = shutil.which("uv") is not None
        if have_uv:
            subprocess.check_call(["uv", "pip", "install", "--upgrade", "pip", "copier"])  # installs into global if no venv activated
            # Ensure copier visible: try binding via the venv python too
            try:
                subprocess.check_call([str(vpy), "-m", "pip", "install", "copier"], stdout=subprocess.DEVNULL)
            except Exception:
                pass
        else:
            subprocess.check_call([str(vpy), "-m", "pip", "install", "--upgrade", "pip", "copier"])

        # Verify
        subprocess.check_call([str(vpy), "-m", "copier", "--version"], stdout=subprocess.DEVNULL)
        return [str(vpy), "-m", "copier"]
    except subprocess.CalledProcessError:
        raise SystemExit(
            "Copier is not available and auto-bootstrap failed. Install with 'pipx install copier' or 'pip install copier' and retry."
        )


def venv_paths(venv_dir: Path) -> tuple[Path, Path]:
    if os.name == "nt":
        python = venv_dir / "Scripts" / "python.exe"
        pip = venv_dir / "Scripts" / "pip.exe"
    else:
        python = venv_dir / "bin" / "python"
        pip = venv_dir / "bin" / "pip"
    return python, pip


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a new project from ml-project-template and set it up.")

    # Resolve robust defaults based on this script's location so callers can
    # run the script from any working directory.
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[1]  # ml-project-template/
    default_template_path = repo_root
    default_parent_dir = repo_root.parent  # parent containing siblings
    parser.add_argument("--name", required=True, help="New project folder name (kebab-case recommended)")
    parser.add_argument(
        "--source",
        choices=["local", "gh"],
        default="local",
        help="Template source: local path (default) or GitHub short URL",
    )
    parser.add_argument(
        "--template-path",
        default=str(default_template_path),
        help="Path to local ml-project-template (used when --source=local). Defaults to the repo containing this script.",
    )
    parser.add_argument(
        "--parent-dir",
        default=str(default_parent_dir),
        help="Parent directory where siblings live (mlcore/, ml-project-template/, and the new project). Defaults to the parent of the template repo.",
    )
    parser.add_argument(
        "--gh-spec",
        default="gh:tristan-day-research/ml-project-template",
        help="GitHub copier spec (used when --source=gh)",
    )
    parser.add_argument(
        "--skip-venv",
        action="store_true",
        help="Skip creating a virtualenv and installing dependencies.",
    )
    parser.add_argument(
        "--mlcore-path",
        default=None,
        help="Explicit path to local mlcore (overrides auto-detection of ../mlcore). If set to 'none', mlcore install is skipped.",
    )
    parser.add_argument(
        "--use-python311",
        action="store_true",
        help="Prefer python3.11 for venv if available; fallback to current interpreter otherwise.",
    )
    # Drop into an interactive shell inside the project with venv activated
    try:
        BoolAction = argparse.BooleanOptionalAction  # py311+
    except AttributeError:  # pragma: no cover - fallback for older pythons
        BoolAction = None  # type: ignore
    if BoolAction:
        parser.add_argument(
            "--enter",
            action=BoolAction,  # type: ignore[arg-type]
            default=True,
            help="Enter an interactive shell in the new project with the venv activated (use --no-enter to disable).",
        )
    else:
        parser.add_argument("--enter", action="store_true", help="Enter an interactive shell in the new project with the venv activated.")
        parser.add_argument("--no-enter", action="store_true", help="Do not enter a shell after setup.")
    parser.add_argument(
        "--shell",
        default=None,
        help="Override shell to spawn (e.g., bash, zsh, fish, cmd, powershell).",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Start the shell without sourcing user rc files (zsh -f, bash --noprofile --norc).",
    )

    args = parser.parse_args(argv)

    parent_dir = Path(args.parent_dir).resolve()
    if not parent_dir.exists():
        parser.error(f"parent dir not found: {parent_dir}")

    # Determine template ref and path
    if args.source == "local":
        template_path = Path(args.template_path).resolve()
        if not template_path.exists():
            parser.error(f"template path not found: {template_path}")
        template_ref = str(template_path)
    else:
        template_ref = args.gh_spec

    # New project dir (will be created by the template as {{ project_slug }})
    project_dir = (parent_dir / args.name).resolve()
    if project_dir.exists() and any(project_dir.iterdir()):
        parser.error(f"target project dir already exists and is not empty: {project_dir}")

    # Prepare env so post_gen can wire local mlcore if present
    env = os.environ.copy()

    # mlcore install strategy (detect early so we can pass env to copier)
    mlcore_path: Path | None
    if args.mlcore_path is not None:
        if args.mlcore_path.lower() == "none":
            mlcore_path = None
        else:
            mlcore_path = Path(args.mlcore_path).resolve()
    else:
        candidate = parent_dir / "mlcore"
        mlcore_path = candidate if candidate.exists() else None

    if mlcore_path and mlcore_path.exists():
        env["MLCORE_LOCAL_PATH"] = str(mlcore_path)

    # Copier copy (interactive prompts by default). Because the template
    # produces a top-level folder named {{ project_slug }}, point the
    # destination to the parent folder and pin project_slug to --name to
    # avoid nested dirs like name/name/.
    print(f"[info] Generating project via Copier → {parent_dir} (slug={args.name})")
    copier_cmd = [
        *find_copier_cmd(repo_root),
        "copy",
        "--trust",
        # Ensure we use the latest template state, not an old git tag
        "--vcs-ref=HEAD",
        "--data",
        f"project_name={args.name}",
        "--data",
        f"project_slug={args.name}",
        template_ref,
        str(parent_dir),
    ]
    run(copier_cmd, env=env)

    # Sanity check: ensure Copier actually generated an answers file and notebooks dir
    answers_file = project_dir / ".copier-answers.yml"
    nbs_dir = project_dir / "lab" / "notebooks"

    if not answers_file.exists():
        print(
            "[warn] .copier-answers.yml not found in the generated project.\n"
            "       This suggests Copier may not have run as expected (or an older Copier version was used).\n"
            "       Verify Copier is >= 9.2: run 'copier --version'."
        )

    if not nbs_dir.exists():
        # Attempt a best-effort local fallback render for notebooks when using the local template.
        # This helps if Copier partially generated the project but skipped these files.
        try:
            if args.source == "local":
                tpl_root = Path(args.template_path).resolve()
                tpl_nbs_dir = tpl_root / "template" / "{{ project_slug }}" / "lab" / "notebooks"
                if tpl_nbs_dir.exists():
                    nbs_dir.mkdir(parents=True, exist_ok=True)
                    pkg_name = args.name.replace("-", "_")
                    for j2 in tpl_nbs_dir.glob("*.ipynb.j2"):
                        target = nbs_dir / j2.name[:-3]  # strip .j2 suffix
                        txt = j2.read_text(encoding="utf-8")
                        # Minimal render: substitute package_name placeholder
                        txt = re.sub(r"{{\s*package_name\s*}}", pkg_name, txt)
                        target.write_text(txt, encoding="utf-8")
                    print(
                        f"[warn] Notebooks directory was missing; wrote fallback notebooks to: {nbs_dir}"
                    )
                else:
                    print(
                        "[warn] Expected template notebooks directory not found at "
                        f"{tpl_nbs_dir} — skipping fallback render."
                    )
            else:
                print(
                    "[warn] Notebooks directory missing and template source was GitHub; "
                    "fallback render requires a local template."
                )
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] Could not create fallback notebooks: {exc}")

    if args.skip_venv:
        print("[info] Skipping venv creation and installs (per --skip-venv)")
        print(f"[done] Project created at: {project_dir}")
        return 0

    # Create venv (prefer 3.11 if asked and available)
    venv_dir = project_dir / ".venv"
    py_for_venv: str
    if args.use_python311:
        py311 = which_python_311()
        py_for_venv = py311 or sys.executable
    else:
        py_for_venv = sys.executable

    print(f"[info] Creating venv with: {py_for_venv}")
    run([py_for_venv, "-m", "venv", str(venv_dir)])
    venv_python, venv_pip = venv_paths(venv_dir)

    # Upgrade pip
    run([str(venv_python), "-m", "pip", "install", "-U", "pip"]) 

    # If MLCORE_LOCAL_PATH env is set, the template's post_gen may wire pyproject.
    # We still allow explicit editable install if mlcore_path is present.
    if mlcore_path and mlcore_path.exists():
        print(f"[info] Installing local mlcore editable: {mlcore_path}")
        run([str(venv_pip), "install", "-e", str(mlcore_path)])
    else:
        print("[info] No local mlcore path provided/detected; skipping editable install.")

    # Install the generated project itself
    print("[info] Installing generated project (editable)")
    run([str(venv_pip), "install", "-e", "."], cwd=project_dir)

    # Enter an interactive shell with venv activated unless disabled
    def spawn_shell() -> None:
        # Change into the project directory for the user session
        os.chdir(project_dir)

        if os.name == "nt":
            # Prefer cmd if available; otherwise try PowerShell
            comspec = os.environ.get("ComSpec")
            if (venv_dir / "Scripts" / "activate.bat").exists():
                activate_bat = str(venv_dir / "Scripts" / "activate.bat")
                shell = comspec or "cmd.exe"
                # /k keeps the shell open
                os.execvp(shell, [shell, "/k", activate_bat])
            else:
                # PowerShell fallback
                ps = "powershell.exe"
                activate_ps1 = str(venv_dir / "Scripts" / "Activate.ps1")
                os.execvp(ps, [ps, "-NoExit", "-Command", f". '{activate_ps1}'"])  # Requires appropriate execution policy
        else:
            # POSIX: detect user shell
            shell_path = args.shell or os.environ.get("SHELL") or "/bin/bash"
            shell_name = Path(shell_path).name

            flags: list[str] = ["-i"]
            if args.clean:
                if shell_name.endswith("fish"):
                    # fish has limited no-config options; fall back to defaults
                    pass
                elif shell_name in {"csh", "tcsh"}:
                    flags = ["-f", "-i"]
                elif shell_name == "zsh":
                    flags = ["-f", "-i"]
                else:  # bash, sh, etc.
                    flags = ["--noprofile", "--norc", "-i"]

            if shell_name.endswith("fish"):
                activate = venv_dir / "bin" / "activate.fish"
            elif shell_name in {"csh", "tcsh"}:
                activate = venv_dir / "bin" / "activate.csh"
            else:
                activate = venv_dir / "bin" / "activate"

            # Source venv and exec a fresh interactive shell with flags
            flags_str = " ".join(flags)
            cmd = f"source '{activate}' && exec {shell_path} {flags_str}"
            os.execvp(shell_path, [shell_path, "-c", cmd])

    # Determine final flag state across both parser variants
    enter = getattr(args, "enter", False)
    if not enter and hasattr(args, "no_enter") and getattr(args, "no_enter"):
        enter = False

    if enter:
        print("\n[enter] Opening an interactive shell in the project with venv activated…")
        spawn_shell()
        return 0  # Unreachable: exec replaces the process, but keep flow explicit
    else:
        print("\n[done] Project ready!")
        print(f"  Location: {project_dir}")
        print(f"  Venv:     {venv_dir}")
        if os.name == "nt":
            print(f"  Activate: {venv_dir / 'Scripts' / 'activate'}")
        else:
            print(f"  Activate: source {venv_dir / 'bin' / 'activate'}")
        print("  Run tests: pytest -q")
        print("  Try a flow: python -m scripts.cli run train-eval")
        print("  Update later: copier update")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
