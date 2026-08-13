from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE = PROJECT_ROOT / "assets" / "ui_audit_console.png"


def test_readmes_open_with_recruiter_summary_and_canonical_ui_image() -> None:
    chinese = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    english = (PROJECT_ROOT / "README_en.md").read_text(encoding="utf-8")

    assert "## 30-second portfolio summary" in english
    assert "## 30 秒作品摘要" in chinese
    assert "[正體中文](README.md)" in english
    assert "[English](README_en.md)" in chinese
    for text in (english, chinese):
        assert "assets/ui_audit_console.png" in text
        assert text.count("```mermaid") == 1
        assert "Group metrics" in text
        for capability in (
            "Model comparison",
            "Probability quality",
            "Explainability",
            "Delivery",
        ):
            assert capability in text
        for marker in ("AUTOGEN:METRICS:START", "AUTOGEN:METRICS:END"):
            assert text.count(marker) == 1


def test_canonical_ui_image_is_small_valid_png() -> None:
    payload = IMAGE.read_bytes()
    assert payload.startswith(b"\x89PNG\r\n\x1a\n")
    assert 50_000 < len(payload) < 5 * 1024 * 1024
