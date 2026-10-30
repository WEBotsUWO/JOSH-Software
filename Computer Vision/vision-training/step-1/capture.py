"""Camera role for Vision Training step 1.

Open the webcam, grab one BGR frame, and stamp it.
Raise RuntimeError when the camera does not open or a read fails.
Timestamp is time.perf_counter() at the grab.
"""

import time

import cv2
import numpy as np


def open_camera(index: int = 0) -> cv2.VideoCapture:
    """Open the webcam at `index`.

    Use cv2.VideoCapture. Raise RuntimeError if isOpened() is false.
    """
    raise NotImplementedError("Camera: open the webcam or raise RuntimeError.")


def read_frame(cap: cv2.VideoCapture) -> tuple[np.ndarray, float]:
    """Return (bgr_frame, timestamp_seconds).

    Call cap.read(). Raise RuntimeError when the read fails.
    Take the timestamp with time.perf_counter() when the frame is grabbed.
    """
    raise NotImplementedError("Camera: return a BGR frame and a perf_counter timestamp.")


if __name__ == "__main__":
    raise SystemExit("Camera: open index 0, read one frame, print its shape and timestamp.")
