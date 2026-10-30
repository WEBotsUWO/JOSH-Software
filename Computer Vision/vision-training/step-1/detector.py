"""Detector role for Vision Training step 1.

Load yolo26n.pt once. Run one BGR frame. Return every class the checkpoint emits.
Class filtering is step 3. Do not drop classes here.

Each dict:
- class_id: int, checkpoint index
- class_name: str, from the model's own names
- confidence: float
- xyxy: list of 4 floats, pixels, origin top-left, x right, y down

Ultralytics: YOLO(weights), then model.predict(frame, verbose=False).
Boxes are on results[0].boxes (cls, conf, xyxy). Names are on model.names.
"""

from typing import Any

import numpy as np


class Detector:
    def __init__(self, weights: str = "yolo26n.pt") -> None:
        """Load `weights` once and keep the model on self."""
        self.weights = weights
        raise NotImplementedError("Detector: load yolo26n.pt once.")

    def detect(self, frame: np.ndarray) -> list[dict[str, Any]]:
        """Return one dict per box. Empty list when the frame has no boxes."""
        raise NotImplementedError("Detector: return class_id, class_name, confidence, xyxy.")


if __name__ == "__main__":
    raise SystemExit("Detector: run one webcam frame or a saved image and print the list.")
