"""Logging setup shared by CLI, tests, and the API."""

from __future__ import annotations

import logging
import sys

_FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"
_DATEFMT = "%H:%M:%S"


def setup_logging(level: str = "INFO") -> None:
    numeric = getattr(logging, level.upper(), None)
    if not isinstance(numeric, int):
        raise ValueError(f"invalid log level: {level!r}")
    logging.basicConfig(
        level=numeric, format=_FORMAT, datefmt=_DATEFMT, stream=sys.stderr, force=True
    )
    # Third-party chatter stays at WARNING.
    for noisy in ("matplotlib", "shap", "urllib3", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
