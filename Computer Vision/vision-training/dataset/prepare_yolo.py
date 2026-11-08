"""Turn the downloaded EgoObjects slice into a YOLO detection set.

Only must-list rows with an EgoObjects name are eligible. Official test images
are ignored. Person, bed, and the prompt-only classes stay out of this head:
yolo26n already has the COCO ones, and YOLOE-26n carries the rest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from collections import defaultdict
from pathlib import Path

from ego_index import ego_name_to_must, load_categories, load_images, load_must_list

IMAGE_SUFFIXES = {".jpg", ".jpeg"}


def yolo_box(bbox: list[float], width: int, height: int):
    x, y, w, h = bbox
    x2, y2 = x + w, y + h
    x = max(0.0, x)
    y = max(0.0, y)
    x2 = min(float(width), x2)
    y2 = min(float(height), y2)
    w = x2 - x
    h = y2 - y
    if w < 1 or h < 1 or width < 1 or height < 1:
        return None
    return ((x + x2) / 2) / width, ((y + y2) / 2) / height, w / width, h / height


def link_or_copy(src: Path, dest: Path) -> None:
    if dest.exists():
        dest.unlink()
    try:
        os.link(src, dest)
    except OSError:
        shutil.copy2(src, dest)


def hold_out(train_items: list[dict]) -> tuple[list[dict], list[dict]]:
    val = []
    kept = []
    for item in train_items:
        digest = hashlib.md5(item["url"].encode("utf-8")).digest()[0]
        if digest % 10 == 0:
            val.append(item)
        else:
            kept.append(item)
    if not val and kept:
        val.append(kept.pop())
    return kept, val


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a YOLO set from the EgoObjects slice.")
    parser.add_argument("--raw", type=Path, default=Path(__file__).resolve().parent / "raw")
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "yolo")
    parser.add_argument("--min-boxes", type=int, default=1, help="Train boxes required before a class enters the head.")
    args = parser.parse_args()

    classes = load_must_list()
    categories = load_categories(args.raw)
    by_category = ego_name_to_must(classes, categories)
    images, boxes = load_images(args.raw)
    on_disk = {path.name: path for path in (args.raw / "images").glob("*") if path.suffix.lower() in IMAGE_SUFFIXES}
    if not on_disk:
        raise SystemExit(f"no images in {args.raw / 'images'}. Run download_subset.py first.")

    grouped = {"train": [], "val": []}
    for name, path in sorted(on_disk.items()):
        record = images.get(name)
        if record is None or record["subset"] == "test":
            continue
        row_boxes = []
        for category_id, bbox in boxes.get(name, []):
            row = by_category.get(category_id)
            if row is None:
                continue
            converted = yolo_box(bbox, record["width"], record["height"])
            if converted is None:
                continue
            row_boxes.append((row["id"], converted))
        if not row_boxes:
            continue
        grouped[record["subset"]].append({"url": name, "path": path, "boxes": row_boxes})

    if not grouped["val"]:
        grouped["train"], grouped["val"] = hold_out(grouped["train"])
        val_source = "held out from train filenames"
    else:
        val_source = "EgoObjects val"
    if not grouped["train"] or not grouped["val"]:
        raise SystemExit("need at least one train image and one val image after the split")

    train_counts = defaultdict(int)
    val_counts = defaultdict(int)
    for item in grouped["train"]:
        for must_id, _box in item["boxes"]:
            train_counts[must_id] += 1
    for item in grouped["val"]:
        for must_id, _box in item["boxes"]:
            val_counts[must_id] += 1

    head = [row for row in classes if row.get("ego") and train_counts[row["id"]] >= args.min_boxes]
    index_of = {row["id"]: index for index, row in enumerate(head)}

    if args.out.exists():
        shutil.rmtree(args.out)
    for split in ("train", "val"):
        (args.out / "images" / split).mkdir(parents=True)
        (args.out / "labels" / split).mkdir(parents=True)

    written = {"train": 0, "val": 0}
    for split, items in grouped.items():
        for item in items:
            lines = []
            for must_id, (cx, cy, bw, bh) in item["boxes"]:
                if must_id not in index_of:
                    continue
                lines.append(f"{index_of[must_id]} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")
            if not lines:
                continue
            stem = Path(item["url"]).stem
            link_or_copy(item["path"], args.out / "images" / split / item["url"])
            (args.out / "labels" / split / f"{stem}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
            written[split] += 1

    names = {index: row["name"] for index, row in enumerate(head)}
    yaml_lines = [
        f"path: {args.out.resolve().as_posix()}",
        "train: images/train",
        "val: images/val",
        "names:",
    ]
    for index, name in names.items():
        yaml_lines.append(f"  {index}: {name}")
    (args.out / "data.yaml").write_text("\n".join(yaml_lines) + "\n", encoding="utf-8")

    report = []
    for row in classes:
        count = train_counts[row["id"]]
        if row["cover"] == "coco":
            status = "yolo26n"
        elif row["cover"] == "prompt":
            status = "yoloe prompt"
        elif row["id"] in index_of:
            status = "in this fine-tune"
        elif count:
            status = "below min-boxes, yoloe prompt"
        else:
            status = "no boxes in this slice, yoloe prompt"
        report.append(
            {
                "id": row["id"],
                "name": row["name"],
                "cover": row["cover"],
                "train_boxes": count,
                "val_boxes": val_counts[row["id"]],
                "status": status,
            }
        )
    summary = {
        "val_source": val_source,
        "images_train": written["train"],
        "images_val": written["val"],
        "head_classes": [row["name"] for row in head],
        "classes": report,
    }
    (args.out / "coverage.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    in_head = sum(1 for row in report if row["status"] == "in this fine-tune")
    print(
        f"YOLO set: {written['train']} train images, {written['val']} val images, "
        f"{in_head} classes in the head ({val_source})"
    )
    missing = [row["name"] for row in report if row["status"].startswith("no boxes")]
    if missing:
        print("no boxes in this slice: " + ", ".join(missing))


if __name__ == "__main__":
    main()
