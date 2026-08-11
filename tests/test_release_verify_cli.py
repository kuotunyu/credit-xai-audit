from __future__ import annotations

from pathlib import Path

import pytest


def test_release_verifier_runs_selected_gate(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from credit_xai.release import verify

    monkeypatch.setattr(verify, "verify_claims", lambda root: ["claim drift"])
    monkeypatch.setattr(verify, "verify_public_tree", lambda root: [])
    monkeypatch.setattr(verify, "verify_release_manifest", lambda root: [])

    assert verify.main(["claims", "--root", str(tmp_path)]) == 1
    assert "claim drift" in capsys.readouterr().err


def test_release_verifier_all_gates_pass(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from credit_xai.release import verify

    monkeypatch.setattr(verify, "verify_claims", lambda root: [])
    monkeypatch.setattr(verify, "verify_public_tree", lambda root: [])
    monkeypatch.setattr(verify, "verify_release_manifest", lambda root: [])

    assert verify.main(["all", "--root", str(tmp_path)]) == 0
    assert "release gates passed" in capsys.readouterr().out
