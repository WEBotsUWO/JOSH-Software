from ultralytics import YOLO

model = YOLO("yolo26x.pt")

results = model.predict(source=0, show=True)
