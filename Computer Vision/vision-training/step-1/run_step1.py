"""Integrator role for Vision Training step 1.

Wire the other six modules. Do not reimplement them.

Loop, in this order:
1. capture.read_frame
2. detector.detect
3. throttle.allow — on False, skip the rest of this iteration
4. messages.FrameDetections
5. overlay.draw
6. log_writer.write

Then cv2.imshow the overlay. Quit on q.

Open the camera with capture.open_camera(0).
Load Detector("yolo26n.pt"). EmitGate defaults to 10 Hz.
Write detections.jsonl in the working directory.

Run from this directory: python run_step1.py
"""

# Keep these imports. Replace main(); it is the function that calls them.
from capture import open_camera, read_frame
from detector import Detector
from log_writer import JsonlLog
from messages import FrameDetections
from overlay import draw
from throttle import EmitGate


def main() -> None:
    """Call the six modules in the module docstring order."""
    raise NotImplementedError(
        "Integrator: wire capture, detector, throttle, messages, overlay, and log_writer."
    )


if __name__ == "__main__":
    main()
