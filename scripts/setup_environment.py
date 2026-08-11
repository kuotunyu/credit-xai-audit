"""Create a portable, CPU-only, non-editable project environment."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _python_path(project_root: Path) -> Path:
    scripts = "Scripts" if sys.platform == "win32" else "bin"
    executable = "python.exe" if sys.platform == "win32" else "python"
    return project_root / ".venv" / scripts / executable


def setup(project_root: Path, include_dev: bool = True) -> None:
    project_root = project_root.resolve()
    for required in ("pyproject.toml", "uv.lock"):
        if not (project_root / required).is_file():
            raise FileNotFoundError(f"{project_root}: missing {required}")
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv is required; install it from https://docs.astral.sh/uv/")

    command = [uv, "sync", "--frozen", "--no-editable"]
    command.extend(["--all-extras", "--group", "dev"] if include_dev else ["--no-dev"])
    environment = os.environ.copy()
    environment.pop("UV_PROJECT_ENVIRONMENT", None)
    environment["CUDA_VISIBLE_DEVICES"] = ""
    subprocess.run(command, cwd=project_root, env=environment, check=True)
    subprocess.run(
        [str(_python_path(project_root)), "-c", "import credit_xai"],
        cwd=project_root,
        env=environment,
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (defaults to the parent of this script)",
    )
    parser.add_argument("--no-dev", action="store_true", help="install runtime dependencies only")
    args = parser.parse_args()
    setup(args.project_root, include_dev=not args.no_dev)


if __name__ == "__main__":
    main()
