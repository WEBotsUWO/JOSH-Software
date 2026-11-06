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
        return {
            "class_id": int(self.class_id),
            "class_name": str(self.class_name),
            "confidence": float(self.confidence),
            "xyxy": [float(v) for v in self.xyxy],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Detection":
        """Build a Detection from those four keys."""
        xyxy = [float(v) for v in data["xyxy"]]
        if len(xyxy) != 4:
            raise ValueError(f"xyxy must have 4 values, got {len(xyxy)}")
        return cls(
            class_id=int(data["class_id"]),
            class_name=str(data["class_name"]),
            confidence=float(data["confidence"]),
            xyxy=xyxy,
        )


@dataclass
class FrameDetections:
    frame_time: float
    emit_time: float
    detections: list[Detection]

    def to_dict(self) -> dict:
        """Return frame_time, emit_time, and detections as dicts."""
        return {
            "frame_time": float(self.frame_time),
            "emit_time": float(self.emit_time),
            "detections": [d.to_dict() for d in self.detections],
        }

    def to_json(self) -> str:
        """One JSON object, no trailing newline. json.dumps(self.to_dict())."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> "FrameDetections":
        """Inverse of to_dict."""
        return cls(
            frame_time=float(data["frame_time"]),
            emit_time=float(data["emit_time"]),
            detections=[Detection.from_dict(d) for d in data.get("detections", [])],
        )


if __name__ == "__main__":
    def _round_trip(record: FrameDetections) -> FrameDetections:
        return FrameDetections.from_dict(json.loads(record.to_json()))

    cases = {
        "two boxes": FrameDetections(
            frame_time=12.345678,
            emit_time=12.350001,
            detections=[
                Detection(0, "person", 0.9123, [10.5, 20.25, 110.0, 220.75]),
                Detection(67, "cell phone", 0.41, [300.0, 150.0, 340.5, 210.0]),
            ],
        ),
        "empty detections": FrameDetections(frame_time=1.0, emit_time=1.1, detections=[]),
    }

    ok = True
    for name, original in cases.items():
        line = original.to_json()
        restored = _round_trip(original)
        same = restored == original
        no_newline = not line.endswith("\n")
        keys_ok = list(json.loads(line).keys()) == ["frame_time", "emit_time", "detections"]
        case_ok = same and no_newline and keys_ok
        ok = ok and case_ok
        print(f"[{'PASS' if case_ok else 'FAIL'}] {name}: {line}")

    print("PASS" if ok else "FAIL")
    raise SystemExit(0 if ok else 1)
