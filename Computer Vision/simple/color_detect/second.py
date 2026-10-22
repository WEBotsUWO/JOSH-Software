import cv2 as cv
import numpy as np

import random
import time

import colornames

from colors import colors
from utils import get_accurate_bbox

# Start with Green in BGR colorspace
bgr_search_color = (0, 255, 0)
rgb_search_color = (
    bgr_search_color[2],
    bgr_search_color[1],
    bgr_search_color[0],
)

prev_frame_time = 0
seconds_to_wait = 10
next_trigger_time = time.time() + seconds_to_wait

cap = cv.VideoCapture(0)

cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Calculate FPS
    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time) if prev_frame_time else 1
    prev_frame_time = new_frame_time

    # Color changer logic
    if new_frame_time >= next_trigger_time:
        rgb_search_color = random.choice(colors)[2]
        bgr_search_color = (
            int(rgb_search_color[2]),
            int(rgb_search_color[1]),
            int(rgb_search_color[0]),
        )
        next_trigger_time = new_frame_time + seconds_to_wait

    # Detect bounding box
    bbox = get_accurate_bbox(frame, bgr_search_color, min_area=300)

    if bbox is not None:
        bbox_arr = np.array(bbox)

        # Handle rotated box array (4 coordinates) vs axis-aligned (4 values)
        if bbox_arr.ndim == 2 and bbox_arr.shape == (4, 2):
            cv.polylines(frame, [bbox_arr], True, bgr_search_color, 3)
        else:
            x1, y1, x2, y2 = bbox
            cv.rectangle(frame, (x1, y1), (x2, y2), bgr_search_color, 3)

    # Display FPS on frame
    cv.putText(
        frame,
        f"FPS: {int(fps)}",
        (5, frame.shape[0] - 10),
        cv.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2,
        cv.LINE_AA,
    )

    # Display search color name on frame
    color_name = str(colornames.find(rgb_search_color))
    cv.putText(
        frame,
        color_name,
        (5, 30),
        cv.FONT_HERSHEY_SIMPLEX,
        1,
        bgr_search_color,
        2,
        cv.LINE_AA,
    )

    cv.imshow("Second Color Detection", frame)

    if cv.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv.destroyAllWindows()
