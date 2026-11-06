"""Load EgoObjects labels and the must-list in classes.yaml.

The Hugging Face copy names the files backwards from the split inside them:
Meta_EgoObjects_Test.json is the train images (no subset field, 78,895 images).
Meta_EgoObjects_Train.json is val and test (subset is "val" or "test").
Trust the subset field. A missing subset is train. subset "test" is never trained on.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CLASSES_PATH = ROOT / "classes.yaml"

# Sizes checked against the mirror on 2026-11-05. A different size means the file changed.
FILES = {
    "categories": ("Meta_EgoObjects_Val.json", 85_217),
    "train_split": ("Meta_EgoObjects_Test.json", 161_152_266),
    "val_and_test": ("Meta_EgoObjects_Train.json", 72_487_045),
}
ZIP_NAME = "Meta_EgoObjects.zip"
ZIP_SIZE = 39_826_913_851
REPO = "https://huggingface.co/datasets/Myszz/EgoObjects/resolve/main/data"

RANK = {"train": 0, "val": 1, "test": 2}


def file_url(name: str) -> str:
    return f"{REPO}/{name}"


def load_must_list(path: Path = CLASSES_PATH) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    classes = data["classes"]
    ids = [item["id"] for item in classes]
    if ids != list(range(len(classes))):
        raise SystemExit(f"{path} ids must be 0..{len(classes) - 1} with no gaps")
    names = [item["name"] for item in classes]
    if len(names) != len(set(names)):
        raise SystemExit(f"{path} has a repeated name")
    return classes


def _read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_categories(raw_dir: Path) -> dict[int, str]:
    path = raw_dir / FILES["categories"][0]
    data = _read_json(path)
    return {int(item["id"]): item["name"] for item in data["categories"]}


def load_images(raw_dir: Path) -> tuple[dict[str, dict], dict[str, list[tuple[int, list]]]]:
    """Return url -> image record, and url -> list of (category_id, bbox).

    bbox is EgoObjects [x, y, width, height] in pixels.
    Records with subset "test" stay in the image map so callers can skip them.
    """
    images: dict[str, dict] = {}
    boxes: dict[str, list[tuple[int, list]]] = defaultdict(list)

    for key in ("train_split", "val_and_test"):
        path = raw_dir / FILES[key][0]
        data = _read_json(path)
        id_to_url: dict[int, str] = {}
        for image in data["images"]:
            url = image["url"]
            subset = image.get("subset") or "train"
            if subset not in RANK:
                raise SystemExit(f"unknown subset {subset!r} on {url}")
            current = images.get(url)
            record = {
                "url": url,
                "subset": subset,
                "width": int(image["width"]),
                "height": int(image["height"]),
                "id": image["id"],
            }
            if current is None or RANK[subset] > RANK[current["subset"]]:
                images[url] = record
            id_to_url[image["id"]] = url
        for ann in data["annotations"]:
            url = id_to_url.get(ann["image_id"])
            if url is None:
                continue
            category = ann.get("category_id", ann.get("_category_id"))
            bbox = ann.get("bbox")
            if category is None or not bbox or len(bbox) != 4:
                continue
            boxes[url].append((int(category), [float(v) for v in bbox]))
        del data
    return images, boxes


def ego_name_to_must(classes: list[dict], categories: dict[int, str]) -> dict[int, dict]:
    """Map an EgoObjects category id onto a must-list row. Unknown ids are omitted."""
    by_ego = {}
    for row in classes:
        ego = row.get("ego")
        if not ego:
            continue
        if ego in by_ego:
            raise SystemExit(f"ego name {ego!r} is on two must-list rows")
        by_ego[ego] = row
    missing = sorted(set(by_ego) - set(categories.values()))
    if missing:
        raise SystemExit("classes.yaml ego names missing from EgoObjects: " + ", ".join(missing))
    id_by_name = {name: cid for cid, name in categories.items()}
    return {id_by_name[name]: row for name, row in by_ego.items()}
