from __future__ import annotations

from pathlib import Path

from credit_xai.release.privacy import verify_public_tree

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_public_tree_verifier_reports_private_content_without_echoing_secrets(
    tmp_path: Path,
) -> None:
    secret = "ghp_" + "a" * 36
    machine_path = "C:" + "\\Users\\someone\\project"
    (tmp_path / "README.md").write_text(f"token={secret}\npath={machine_path}\n", encoding="utf-8")
    (tmp_path / "PROGRESS.md").write_text("private handoff\n", encoding="utf-8")
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "raw.csv").write_text("private row\n", encoding="utf-8")
    (tmp_path / "models").mkdir()
    (tmp_path / "models" / "model.joblib").write_bytes(b"pickle")
    (tmp_path / "oversized.bin").write_bytes(b"0" * (5 * 1024 * 1024 + 1))

    errors = verify_public_tree(tmp_path)
    report = "\n".join(errors)

    for category in (
        "credential",
        "machine-specific path",
        "private note",
        "raw dataset",
        "model payload",
        "large file",
    ):
        assert category in report
    assert secret not in report


def test_public_tree_verifier_accepts_small_public_files(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("Historical educational audit.\n", encoding="utf-8")
    (tmp_path / "models").mkdir()
    (tmp_path / "models" / ".gitkeep").write_text("", encoding="utf-8")

    assert verify_public_tree(tmp_path) == []


def test_public_tree_verifier_does_not_flag_its_own_source() -> None:
    release_package = PROJECT_ROOT / "src" / "credit_xai" / "release"

    assert verify_public_tree(release_package) == []
