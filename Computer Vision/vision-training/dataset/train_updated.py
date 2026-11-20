"""Fine-tune yolo26n on the prepared EgoObjects slice.

Writes runs/josh-ego. Does not replace vision-training/yolo26n.pt.
That checkpoint stays the step-1 detector. This head only contains classes
the slice actually labeled.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _parse_cache(value: str | None) -> bool | str | None:
    if value is None:
        return None
    lowered = value.strip().lower()
    if lowered in {"false", "0", "none", "off"}:
        return False
    if lowered in {"true", "1", "on"}:
        return True
    return lowered


def main() -> None:
    default_workers = 4 if os.name == "nt" else 8

    parser = argparse.ArgumentParser(description="Fine-tune yolo26n on dataset/yolo.")
    parser.add_argument("--data", type=Path, default=Path(__file__).resolve().parent / "yolo" / "data.yaml")
    parser.add_argument("--weights", type=Path, default=ROOT / "yolo26n.pt")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--patience", type=int, default=20)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default=None, help="Ultralytics device, for example 0. Omit to let it choose.")
    parser.add_argument("--name", default="josh-ego")
    parser.add_argument(
        "--workers",
        type=int,
        default=default_workers,
        help=f"DataLoader worker processes (default: {default_workers}). Try 0, 2, 4, or 6 on Windows.",
    )
    parser.add_argument(
        "--cache",
        default=None,
        help="Image cache mode: 'ram', 'disk', 'false', or omit for Ultralytics default.",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Disable per-epoch plot generation to save overhead during long runs.",
    )
    parser.add_argument(
        "--val-every",
        type=int,
        default=1,
        help="Run validation every N epochs (default: 1 = every epoch). Always validates on the final epoch.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from runs/<name>/weights/last.pt if available.",
    )
    args = parser.parse_args()

    if args.val_every < 1:
        raise SystemExit("--val-every must be >= 1.")

    if not args.data.is_file():
        raise SystemExit(f"missing {args.data}. Run prepare_yolo.py first.")

    coverage_path = args.data.parent / "coverage.json"
    if coverage_path.is_file():
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        left = [row["name"] for row in coverage["classes"] if row["status"] != "in this fine-tune"]
        print(f"head: {', '.join(coverage['head_classes']) or '(empty)'}")
        print("left on yolo26n or YOLOE-26n: " + ", ".join(left))

    from ultralytics import YOLO

    run_dir = ROOT / "runs" / args.name
    last_ckpt = run_dir / "weights" / "last.pt"

    if args.resume:
        if not last_ckpt.is_file():
            raise SystemExit(f"--resume requested, but checkpoint not found at {last_ckpt}.")
        weights = last_ckpt
    else:
        weights = args.weights if args.weights.is_file() else Path("yolo26n.pt")

    model = YOLO(str(weights))

    # When --val-every > 1, skip Ultralytics' default per-epoch validation pass
    # and run validation only every N epochs (and on the final epoch).
    run_inline_val = args.val_every == 1

    if not run_inline_val:
        def _periodic_val(trainer) -> None:
            epoch_num = trainer.epoch + 1
            is_interval = (epoch_num % args.val_every) == 0
            is_last = epoch_num == trainer.epochs
            if is_interval or is_last:
                trainer.val = True
                trainer.validate()
            else:
                trainer.val = False

        model.add_callback("on_fit_epoch_end", _periodic_val)

    train_args: dict[str, object] = {
        "data": str(args.data),
        "epochs": args.epochs,
        "patience": args.patience,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "workers": args.workers,
        "project": str(ROOT / "runs"),
        "name": args.name,
        "exist_ok": True,
        "pretrained": not args.resume,
        "warmup_epochs": 1,
        "plots": not args.no_plots,
        "val": run_inline_val,
        "resume": args.resume,
    }

    parsed_cache = _parse_cache(args.cache)
    if parsed_cache is not None:
        train_args["cache"] = parsed_cache

    if args.device is not None:
        train_args["device"] = args.device

    model.train(**train_args)
    print(f"weights are under {run_dir}. yolo26n.pt was not replaced.")


if __name__ == "__main__":
    main()
