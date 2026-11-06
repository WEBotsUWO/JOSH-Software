"""Ask YOLOE-26n for every class in classes.yaml.

This is how the full list is nameable before the fine-tune has boxes for it.
The first call downloads yoloe-26n-seg.pt and a text encoder.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ego_index import load_must_list


def main() -> None:
    parser = argparse.ArgumentParser(description="Prompt YOLOE-26n with the must-list.")
    parser.add_argument("--image", type=Path, help="Image to run. Omit with --list.")
    parser.add_argument("--list", action="store_true", help="Print the must-list and exit.")
    parser.add_argument("--weights", default="yoloe-26n-seg.pt")
    args = parser.parse_args()

    classes = load_must_list()
    if args.list or args.image is None:
        for row in classes:
            print(f"{row['id']:3d}  {row['name']}  [{row['cover']}]")
        if args.image is None:
            return

    from ultralytics import YOLOE

    model = YOLOE(args.weights)
    model.set_classes([row["prompt"] for row in classes])
    results = model.predict(str(args.image), verbose=False)
    boxes = results[0].boxes
    if boxes is None or len(boxes) == 0:
        print("no boxes")
        return
    for cls, conf, xyxy in zip(boxes.cls.tolist(), boxes.conf.tolist(), boxes.xyxy.tolist()):
        row = classes[int(cls)]
        x1, y1, x2, y2 = (round(v, 1) for v in xyxy)
        print(f"{row['name']}  {conf:.2f}  {x1} {y1} {x2} {y2}")


if __name__ == "__main__":
    main()
