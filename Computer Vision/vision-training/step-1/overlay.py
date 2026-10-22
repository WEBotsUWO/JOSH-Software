"""Overlay role for Vision Training step 1.

Copy the frame, draw on the copy, return the copy.
Do not call imshow. The integrator owns the window.

Draw each box with class_name and confidence.
Draw camera_fps and emit_hz on the image so both rates are visible.
"""

import cv2
import numpy as np

from messages import FrameDetections


def draw(
    frame: np.ndarray,
    record: FrameDetections,
    camera_fps: float,
    emit_hz: float,
) -> np.ndarray:
    """Return a new image. Leave `frame` unchanged.

    cv2.rectangle and cv2.putText are enough.
    """
    raise NotImplementedError("Overlay: draw class, confidence, camera FPS, and emit Hz.")


if __name__ == "__main__":
    raise SystemExit("Overlay: draw one fake FrameDetections on a blank image and show it.")
