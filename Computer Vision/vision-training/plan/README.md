# Vision Training plan

[Back to the team list](../README.md)

## What we are building

A detector the RL team can trust. Three stages, in this order:

1. A pretrained YOLO26n checkpoint that already detects many classes.
2. A weight update for JOSH classes that checkpoint does not have.
3. A ROS 2 publish of the detection record at 10 Hz until the software lead confirms a different number.

The laptop stream in step 1 is how we learn the record before any of that gets expensive.

## Why pretrained first

COCO-scale YOLO already covers person, sports ball, chairs, and most of a gym. Student machines can run `yolo26n.pt`. They are a poor place to train a detector from scratch. The fine-tune in step 5 is for the classes that checkpoint misses: rim, hoop, and a grasp label if we have images for it.

## Why the record comes before ROS 2

ROS 2 is the transport. The fields are the contract: class id, class name, confidence, `xyxy`, frame time, emit time. Step 2 writes those fields down so the ROS message in step 7 cannot grow a second schema. Step 1's `messages.py` is the draft of that contract.

## Why 10 Hz

The camera can run faster than the RL team can use. We drop frames on purpose and publish a steady record. 10 Hz is the working number. Change it in one place (`EmitGate` in step 1, and later the ROS node) after the software lead confirms.

## Why tracking is step 4

Ids need a stable detection schema first. ByteTrack (or Ultralytics' tracker, which uses the same idea) keeps one id through blur and a short occlusion. Until step 4, RL gets detections, and the record has no track id.

## What step 1 leaves alone

Class filtering, training, ROS 2, and the basketball success bits in [docs/06-basketball-task.md](../../docs/06-basketball-task.md). Those have later step numbers.
