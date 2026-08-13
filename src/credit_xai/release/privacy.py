"""Fail-closed scan of the files intended for the public repository."""

from __future__ import annotations

import re
from pathlib import Path

MAX_PUBLIC_FILE_BYTES = 5 * 1024 * 1024
_IGNORED_ROOTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "build",
    "dist",
    "tmp",
}
_TEXT_SUFFIXES = {
    "",
    ".cff",
    ".cfg",
    ".csv",
    ".json",
    ".jsonl",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
_PRIVATE_NAMES = re.compile(r"(?i)(progress|handoff|hand-over|agent[_-]?notes?|private[_-]?notes?)")
_CREDENTIAL_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(
        r"(?i)(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*"
        r"['\"][^'\"]{8,}['\"]"
    ),
)
_MACHINE_PATH_PATTERNS = (
    re.compile(r"(?i)[A-Z]:[\\/]Users[\\/]"),
    re.compile(r"/(?:home|Users)/[^/\s]+/"),
    re.compile("(?i)file:" + "//"),
)


def _ignored(relative: Path) -> bool:
    return any(part in _IGNORED_ROOTS or part.startswith(".venv") for part in relative.parts)


def verify_public_tree(root: str | Path) -> list[str]:
    """Return redacted privacy/content violations under ``root``."""
    root = Path(root).resolve()
    errors: list[str] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if _ignored(relative):
            continue
        display = relative.as_posix()
        if path.is_symlink():
            errors.append(f"{display}: symbolic link is outside the public artifact policy")
            continue
        if not path.is_file():
            continue
        if _PRIVATE_NAMES.search(display):
            errors.append(f"{display}: private note filename is forbidden")
        if relative.parts and relative.parts[0].lower() == "data":
            errors.append(f"{display}: raw dataset content is forbidden")
        if relative.parts and relative.parts[0].lower() == "models" and relative.name != ".gitkeep":
            errors.append(f"{display}: model payload is forbidden")
        if path.stat().st_size > MAX_PUBLIC_FILE_BYTES:
            errors.append(
                f"{display}: large file exceeds {MAX_PUBLIC_FILE_BYTES // (1024 * 1024)} MiB"
            )
        if path.suffix.lower() not in _TEXT_SUFFIXES or path.stat().st_size > MAX_PUBLIC_FILE_BYTES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in _CREDENTIAL_PATTERNS):
                errors.append(f"{display}:{line_number}: credential pattern detected (redacted)")
            if any(pattern.search(line) for pattern in _MACHINE_PATH_PATTERNS):
                errors.append(f"{display}:{line_number}: machine-specific path detected (redacted)")
    return errors
