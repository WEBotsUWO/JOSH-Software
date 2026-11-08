"""Webcam check for Vision Training. The assignment is ../step-1/.

Uses yolo26n.pt (small). simple/people_detect/main.py still uses yolo26x.pt.
Ultralytics downloads the file on first run. Offline, load
../../simple/people_detect/yolo26n.pt instead.
"""

from ultralytics import YOLO


model = YOLO("yolo26n.pt")

model.train(
    data=r"C:\Users\cryog\Documents\GitHub\JOSH-Software\Computer Vision\vision-training\examples\Update820\data.yaml", 
    epochs=50, 
    imgsz=640,
    device="cpu"
)
##.venv\Scripts\Activate.ps1
##deactivate after working
