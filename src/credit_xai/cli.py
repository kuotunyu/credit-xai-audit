"""Command-line interface. Thin dispatcher only — all logic lives in step modules.

Usage::

    python -m credit_xai.cli data prepare --config configs/smoke.yaml
    python -m credit_xai.cli train --model logistic --config configs/smoke.yaml
    python -m credit_xai.cli calibrate --config configs/smoke.yaml
    python -m credit_xai.cli explain --config configs/smoke.yaml
    python -m credit_xai.cli evaluate --config configs/smoke.yaml
    python -m credit_xai.cli report --config configs/smoke.yaml
    python -m credit_xai.cli serve --config configs/smoke.yaml
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Callable
from typing import cast

from credit_xai import __version__
from credit_xai.config import Config, load_config
from credit_xai.constants import MODEL_NAMES
from credit_xai.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", required=True, help="path to a YAML config file")
    parser.add_argument("--log-level", default="INFO", help="logging level (default INFO)")


def _model_arg(parser: argparse.ArgumentParser, required: bool) -> None:
    parser.add_argument(
        "--model",
        choices=list(MODEL_NAMES),
        required=required,
        default=None if required else "all",
        help="model to operate on" + ("" if required else " (default: all trained models)"),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="credit-xai",
        description=(
            "Historical 2005 educational XAI audit of the UCI credit default dataset. "
            "Not for lending decisions. Not financial advice."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_data = sub.add_parser("data", help="dataset operations")
    data_sub = p_data.add_subparsers(dest="subcommand", required=True)
    p_prepare = data_sub.add_parser("prepare", help="download, clean, split, write manifests")
    _common(p_prepare)
    p_prepare.add_argument(
        "--force", action="store_true", help="re-run even if processed data exists"
    )
    p_prepare.set_defaults(func=_cmd_data_prepare)

    p_train = sub.add_parser("train", help="fit one model on the train split")
    _common(p_train)
    _model_arg(p_train, required=True)
    p_train.set_defaults(func=_cmd_train)

    p_cal = sub.add_parser("calibrate", help="fit calibrators on validation, select winner")
    _common(p_cal)
    _model_arg(p_cal, required=False)
    p_cal.set_defaults(func=_cmd_calibrate)

    p_explain = sub.add_parser("explain", help="run the XAI suite")
    _common(p_explain)
    _model_arg(p_explain, required=False)
    p_explain.add_argument("--resume", action="store_true", help="resume partial checkpoints")
    p_explain.add_argument("--force", action="store_true", help="discard partial checkpoints")
    p_explain.set_defaults(func=_cmd_explain)

    p_eval = sub.add_parser("evaluate", help="test metrics with bootstrap CIs + group snapshot")
    _common(p_eval)
    _model_arg(p_eval, required=False)
    p_eval.add_argument("--resume", action="store_true", help="resume partial checkpoints")
    p_eval.add_argument("--force", action="store_true", help="discard partial checkpoints")
    p_eval.set_defaults(func=_cmd_evaluate)

    p_report = sub.add_parser("report", help="aggregate raw results into summary.json + README")
    _common(p_report)
    p_report.set_defaults(func=_cmd_report)

    p_serve = sub.add_parser("serve", help="start the FastAPI app (Gradio UI mounted at /ui)")
    _common(p_serve)
    p_serve.add_argument("--host", default=None, help="override serve.host")
    p_serve.add_argument("--port", type=int, default=None, help="override serve.port")
    p_serve.set_defaults(func=_cmd_serve)

    return parser


def _load(args: argparse.Namespace) -> Config:
    setup_logging(args.log_level)
    cfg = load_config(args.config)
    logger.info(
        "loaded config %s (run=%s, hash=%s...)", args.config, cfg.run.name, cfg.config_hash[:12]
    )
    return cfg


def _models(args: argparse.Namespace) -> list[str]:
    return list(MODEL_NAMES) if args.model in (None, "all") else [args.model]


# -- command handlers (lazy imports keep startup fast and optional deps optional) --


def _cmd_data_prepare(args: argparse.Namespace) -> int:
    from credit_xai.data.prepare import run as prepare_run

    prepare_run(_load(args), force=args.force)
    return 0


def _cmd_train(args: argparse.Namespace) -> int:
    from credit_xai.training.train import run as train_run

    train_run(_load(args), model_name=args.model)
    return 0


def _cmd_calibrate(args: argparse.Namespace) -> int:
    from credit_xai.calibration.calibrate import run as calibrate_run

    cfg = _load(args)
    for name in _models(args):
        calibrate_run(cfg, model_name=name)
    return 0


def _cmd_explain(args: argparse.Namespace) -> int:
    from credit_xai.explain.run import run as explain_run

    cfg = _load(args)
    for name in _models(args):
        explain_run(cfg, model_name=name, resume=args.resume, force=args.force)
    return 0


def _cmd_evaluate(args: argparse.Namespace) -> int:
    from credit_xai.evaluation.evaluate import run as evaluate_run

    cfg = _load(args)
    for name in _models(args):
        evaluate_run(cfg, model_name=name, resume=args.resume, force=args.force)
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    from credit_xai.reporting.run import run as report_run

    report_run(_load(args))
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    from credit_xai.serving.launch import run as serve_run

    cfg = _load(args)
    serve_run(cfg, host=args.host, port=args.port)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        handler = cast(Callable[[argparse.Namespace], int], args.func)
        return handler(args)
    except KeyboardInterrupt:
        logger.warning("interrupted — checkpointed steps can be resumed with --resume")
        return 130
    except Exception as exc:  # single choke point: readable errors, non-zero exit
        logger.error("%s: %s", type(exc).__name__, exc)
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            raise
        return 1


if __name__ == "__main__":
    sys.exit(main())
