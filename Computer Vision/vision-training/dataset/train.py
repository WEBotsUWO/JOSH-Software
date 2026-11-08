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


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune yolo26n on dataset/yolo.")
    parser.add_argument("--data", type=Path, default=Path(__file__).resolve().parent / "yolo" / "data.yaml")
    parser.add_argument("--weights", type=Path, default=ROOT / "yolo26n.pt")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--patience", type=int, default=20)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default=None, help="Ultralytics device, for example 0. Omit to let it choose.")
    parser.add_argument("--name", default="josh-ego")
    args = parser.parse_args()

    if not args.data.is_file():
        raise SystemExit(f"missing {args.data}. Run prepare_yolo.py first.")
    coverage_path = args.data.parent / "coverage.json"
    if coverage_path.is_file():
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        left = [row["name"] for row in coverage["classes"] if row["status"] != "in this fine-tune"]
        print(f"head: {', '.join(coverage['head_classes']) or '(empty)'}")
        print("left on yolo26n or YOLOE-26n: " + ", ".join(left))

    from ultralytics import YOLO

    weights = args.weights if args.weights.is_file() else Path("yolo26n.pt")
    model = YOLO(str(weights))
    train_args = {
        "data": str(args.data),
        "epochs": args.epochs,
        "patience": args.patience,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "workers": 0 if os.name == "nt" else 8,
        "project": str(ROOT / "runs"),
        "name": args.name,
        "exist_ok": True,
        "pretrained": True,
        "warmup_epochs": 1,
    }
    if args.device is not None:
        train_args["device"] = args.device
    model.train(**train_args)
    print(f"weights are under {ROOT / 'runs' / args.name}. yolo26n.pt was not replaced.")


if __name__ == "__main__":
    main()
