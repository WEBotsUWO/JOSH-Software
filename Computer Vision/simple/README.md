# Practice sketches

These are intros. Robot work goes in [Vision Training](../vision-training/README.md) and [Vector Navigation](../vector-navigation/README.md).

| Folder | What it shows |
| --- | --- |
| `color_detect/` | HSV threshold, a box around one color, webcam |
| `watershed_segmentation/` | Classic watershed on one photo |
| `people_detect/` | Ultralytics YOLO on the webcam. `main.py` loads `yolo26x.pt`, the large checkpoint |

Vision Training uses `yolo26n.pt`, the small checkpoint, so a laptop can hold it. Leave `people_detect/main.py` on `yolo26x.pt`.
