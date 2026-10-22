"""Schema role for Vision Training step 1.

The field names are the contract. JSON has to round-trip them.
Step 2 freezes this shape for ROS 2, so keep the keys stable.

FrameDetections JSON:
{
  "frame_time": float,
  "emit_time": float,
  "detections": [
    {"class_id": int, "class_name": str, "confidence": float, "xyxy": [x1, y1, x2, y2]}
  ]
}

xyxy is pixels, origin top-left. An empty detections list is valid.
"""

import json
from dataclasses import dataclass


@dataclass
class Detection:
    class_id: int
    class_name: str
    confidence: float
    xyxy: list[float]

    def to_dict(self) -> dict:
        """Return the four keys in the module docstring."""
        raise NotImplementedError("Schema: Detection.to_dict")

    @classmethod
    def from_dict(cls, data: dict) -> "Detection":
        """Build a Detection from those four keys."""
        raise NotImplementedError("Schema: Detection.from_dict")


@dataclass
class FrameDetections:
    frame_time: float
    emit_time: float
    detections: list[Detection]

    def to_dict(self) -> dict:
        """Return frame_time, emit_time, and detections as dicts."""
        raise NotImplementedError("Schema: FrameDetections.to_dict")

    def to_json(self) -> str:
        """One JSON object, no trailing newline. json.dumps(self.to_dict())."""
        raise NotImplementedError("Schema: FrameDetections.to_json")

    @classmethod
    def from_dict(cls, data: dict) -> "FrameDetections":
        """Inverse of to_dict."""
        raise NotImplementedError("Schema: FrameDetections.from_dict")


if __name__ == "__main__":
    raise SystemExit("Schema: build one FrameDetections, to_json, from_dict, compare fields.")
