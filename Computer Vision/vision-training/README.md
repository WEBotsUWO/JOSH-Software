# Vision Training

YOLO on camera images. Pretrained first, then our weights, then a stream the RL team can subscribe to.

[Back to the map](../README.md)

The CV lead owns this order and the detection record. Developers own the files named in the current step.

## Steps

Finish these before calling the system ready for RL integration. The publish rate is 10 Hz until the software lead confirms a different number.

1. **Laptop detection stream.** Assigned now. Pretrained `yolo26n.pt` on the webcam, every class the checkpoint already has, a versioned detection record, emit capped at 10 Hz, on-screen boxes, JSONL log. Step 1 stops at the laptop log. Fine-tune is step 5. ROS 2 is step 7. Files and roles: [step-1](step-1/README.md).
2. Freeze that record (class id, name, confidence, `xyxy`, frame time, emit time) so the ROS 2 message uses the same fields.
3. Write the JOSH class subset (person, sports ball, and whatever else this semester needs) as a filter. Keep the pretrained head.
4. Add tracking (Ultralytics track / ByteTrack) so a short occlusion keeps one id.
5. Fine-tune weights only for classes COCO cannot do (rim, hoop, and any grasp label we actually need). Train by updating the pretrained checkpoint. A from-scratch detector is out of scope.
6. Score a tiny labeled set and write the failure modes.
7. ROS 2 publisher of that same record at 10 Hz, plus a debug image topic. Leave the rate provisional until the software lead confirms it.
8. RL subscribes and sees boxes at that rate. This list is done when that subscription works without a CV developer in the loop.

## In this folder

| Path | What it is |
| --- | --- |
| [plan](plan/README.md) | Why this order |
| [structure](structure/README.md) | Modules and the detection record |
| [examples/webcam_yolo.py](examples/webcam_yolo.py) | Short check that the webcam and `yolo26n.pt` work |
| [step-1](step-1/README.md) | Current assignment |

Install once, from this folder:

```
pip install -r requirements.txt
```

Ultralytics downloads `yolo26n.pt` on first run. Offline, point the loader at `simple/people_detect/yolo26n.pt`. Weights and `detections.jsonl` stay out of git.
