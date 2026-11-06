"""Webcam check for Vision Training. The assignment is ../step-1/.

Uses yolo26n.pt (small). simple/people_detect/main.py still uses yolo26x.pt.
Ultralytics downloads the file on first run. Offline, load
../../simple/people_detect/yolo26n.pt instead.
"""

from ultralytics import YOLO

model = YOLO("yolo26n.pt")
model.predict(source=0, show=True)
