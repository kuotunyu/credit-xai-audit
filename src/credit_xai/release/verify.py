"""Command-line release gates for the public repository."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from credit_xai.release.claims import verify_claims
from credit_xai.release.manifest import verify_release_manifest
from credit_xai.release.privacy import verify_public_tree

Gate = Callable[[str | Path], list[str]]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "gate",
        choices=("all", "claims", "privacy", "manifest"),
        nargs="?",
        default="all",
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    gates: dict[str, Gate] = {
        "claims": verify_claims,
        "privacy": verify_public_tree,
        "manifest": verify_release_manifest,
    }
    selected = gates.items() if args.gate == "all" else ((args.gate, gates[args.gate]),)
    failures: list[str] = []
    for name, gate in selected:
        failures.extend(f"{name}: {error}" for error in gate(args.root))
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print(f"release gates passed: {args.gate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
