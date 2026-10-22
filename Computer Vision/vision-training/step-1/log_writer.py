"""Logger role for Vision Training step 1.

Append one JSON object per emitted frame to detections.jsonl.
Use record.to_json(), then a newline. Flush so a tail of the file
updates during a run. Append, so a second run keeps the earlier lines.
"""

from messages import FrameDetections


class JsonlLog:
    def __init__(self, path: str = "detections.jsonl") -> None:
        self.path = path

    def write(self, record: FrameDetections) -> None:
        """Append one line and flush."""
        raise NotImplementedError("Logger: append record.to_json() and a newline, then flush.")

    def close(self) -> None:
        """Close the file if you kept it open. Safe to call more than once."""
        raise NotImplementedError("Logger: close the log.")


if __name__ == "__main__":
    raise SystemExit("Logger: write one fake record and print the line from detections.jsonl.")
