import cv2 as cv
import numpy as np


def get_limits(color):
    c = np.uint8([[color]])
    hsvC = cv.cvtColor(c, cv.COLOR_BGR2HSV)

    # Cast the specific hue value to a standard python int
    hue = int(hsvC[0][0][0])

    lower_limit = [np.clip(hue - 10, 0, 179), 100, 100]
    upper_limit = [np.clip(hue + 10, 0, 179), 255, 255]

    lower_limit = np.array(lower_limit, dtype=np.uint8)
    upper_limit = np.array(upper_limit, dtype=np.uint8)

    return lower_limit, upper_limit


def get_hsv_limits(bgr_color, hue_sensitivity=15, sat_min=40, val_min=40):
    """Calculates HSV ranges with forgiving Saturation/Value bounds for webcams."""
    c = np.uint8([[bgr_color]])
    hsvC = cv.cvtColor(c, cv.COLOR_BGR2HSV)
    hue = int(hsvC[0][0][0])

    lower_h = hue - hue_sensitivity
    upper_h = hue + hue_sensitivity

    ranges = []

    # Handle red/hue wraparound at boundaries (0 and 179)
    if lower_h < 0:
        ranges.append(
            (
                np.array([180 + lower_h, sat_min, val_min], dtype=np.uint8),
                np.array([179, 255, 255], dtype=np.uint8),
            )
        )
        ranges.append(
            (
                np.array([0, sat_min, val_min], dtype=np.uint8),
                np.array([upper_h, 255, 255], dtype=np.uint8),
            )
        )
    elif upper_h > 179:
        ranges.append(
            (
                np.array([lower_h, sat_min, val_min], dtype=np.uint8),
                np.array([179, 255, 255], dtype=np.uint8),
            )
        )
        ranges.append(
            (
                np.array([0, sat_min, val_min], dtype=np.uint8),
                np.array([upper_h - 180, sat_min, val_min], dtype=np.uint8),
            )
        )
    else:
        ranges.append(
            (
                np.array([lower_h, sat_min, val_min], dtype=np.uint8),
                np.array([upper_h, 255, 255], dtype=np.uint8),
            )
        )

    return ranges


def get_accurate_bbox(
    frame,
    bgr_search_color,
    min_area=300,
    hue_sensitivity=15,
    sat_min=40,
    val_min=40,
):
    # Apply Gaussian Blur to smooth out camera noise before converting spaces
    blurred = cv.GaussianBlur(frame, (5, 5), 0)
    hsvImage = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)

    ranges = get_hsv_limits(
        bgr_search_color,
        hue_sensitivity=hue_sensitivity,
        sat_min=sat_min,
        val_min=val_min,
    )
    mask = np.zeros(hsvImage.shape[:2], dtype=np.uint8)

    for lower, upper in ranges:
        mask = cv.bitwise_or(mask, cv.inRange(hsvImage, lower, upper))

    # Lightweight noise cleaning (3x3 kernel so cube stickers aren't erased)
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)

    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # Option 1: Find all valid contours and draw a combined box around the full side
    valid_contours = [c for c in contours if cv.contourArea(c) >= min_area]

    if not valid_contours:
        return None

    # Merge all valid color contours into one big bounding box (covers all 9 stickers)
    all_points = np.vstack(valid_contours)
    x, y, w, h = cv.boundingRect(all_points)

    return (x, y, x + w, y + h)
