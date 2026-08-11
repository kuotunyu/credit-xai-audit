from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.installation
def test_non_editable_install_imports_from_unicode_checkout(tmp_path: Path) -> None:
    checkout = tmp_path / "公開候選"
    checkout.mkdir()
    for directory in ("src",):
        shutil.copytree(PROJECT_ROOT / directory, checkout / directory)
    for filename in ("pyproject.toml", "uv.lock", "README.md", "LICENSE"):
        shutil.copy2(PROJECT_ROOT / filename, checkout / filename)

    setup_script = PROJECT_ROOT / "scripts" / "setup_environment.py"
    subprocess.run(
        [sys.executable, str(setup_script), "--project-root", str(checkout), "--no-dev"],
        check=True,
        cwd=tmp_path,
    )

    scripts_dir = checkout / ".venv" / ("Scripts" if sys.platform == "win32" else "bin")
    python = scripts_dir / ("python.exe" if sys.platform == "win32" else "python")
    site_packages = next((checkout / ".venv").glob("Lib/site-packages"))
    pth_text = "\n".join(path.read_text(encoding="utf-8") for path in site_packages.glob("*.pth"))
    assert str(checkout / "src") not in pth_text

    completed = subprocess.run(
        [str(python), "-c", "import credit_xai; print(credit_xai.__version__)"],
        check=True,
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.strip() == "0.1.0"
