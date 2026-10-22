# Computer vision that actually ships on a humanoid

Academic CV is a catalog of tasks. JOSH only needs a small set, done with engineering discipline: calibrated cameras, known frames, timed messages, and detectors you can trust enough to write rewards on.

[Back to README](../README.md)

## Geometry first, models second

A detector that says "ball at pixel (u, v)" is useless for walking or grasping until you can say where that is in the robot's body frame. That requires camera **intrinsics** (focal length, principal point, distortion), **extrinsics** (where the camera sits on the head/wrist), and a TF tree from `camera_optical_frame` → head → torso → world.

If those three are wrong, every later model looks dumb.

| Concept | Why JOSH cares | Typical artifact |
| --- | --- | --- |
| Intrinsics | Pixels → rays. Wrong K matrix makes every 3D estimate drift | `camera_info` / YAML from calibration |
| Extrinsics / TF | Head camera moves when the neck moves. Wrist cameras move with arms | URDF + `robot_state_publisher` + static or calibrated camera mount |
| Time sync | Image at t vs joints at t+40ms looks like the ball is offset | ROS timestamps, ApproximateTimeSynchronizer, hardware sync if possible |
| Distortion / rolling shutter | Wide FOV and walking = bent rims and smeared balls | Calibrate; prefer global shutter if budget allows |

## Closed-set vs open-world

### Closed-set detectors

The first model is a pretrained YOLO26n checkpoint. It already names a large set of COCO classes. That is what [Vision Training](../vision-training/README.md) step 1 runs on a laptop camera.

Update the weights later for JOSH classes the checkpoint cannot do: rim, hoop, and any grasp label we actually need. A from-scratch detector is out of scope on student GPUs.

Use the pretrained checkpoint for anything that must run this year. Fine-tune the classes it misses. That fine-tune is step 5 on the Vision Training list.

### Open-vocabulary

Grounding DINO, SAM, CLIP, or the VLM inside GR00T. "Find the orange ball-like object." Flexible, slower, easier to fool.

Use this for exploration and language, not as the only hoop success detector.

## Tracking is not optional

Detection is per-frame. The robot lives in time. Grasp and walk controllers should subscribe to **tracks**, not raw detections. A flickering box must become a stable `ball #3`.

The first code is the pretrained detector: [Vision Training](../vision-training/README.md) steps 1–3. ByteTrack is step 4, after that detection record exists.

The basketball graph tracks a ball and a rim in the same image, and the first box comes from the detector. ByteTrack associates every detection, including low-confidence ones, so motion blur and a short occlusion keep the same id. Those are the failures already listed on the [basketball task](06-basketball-task.md): occlusion, blur while walking, the ball leaving the hand.

Cameras run at 15–30 Hz. The detector publish target is 10 Hz until the software lead confirms a different number ([rates](05-ros2-isaac.md)). Holding hundreds of frames per second in the tracker does not help. Dropped ids do.

| Method | Fit for JOSH |
| --- | --- |
| YOLO + ByteTrack | Default. Several objects, boxes from the detector, ids held through blur and a brief occlusion. |
| YOLO + SORT / OC-SORT | Downgrade when the on-robot machine cannot hold detector rate. A Kalman filter is cheap; a long occlusion mints a new id. |
| DeepSORT / StrongSORT | Motion plus an appearance network. Useful when many similar people must stay distinct. Ball and rim are different classes; skip the extra network this year. |
| CSRT | One object, box drawn by a person, accuracy ahead of frame rate. A notebook experiment, not the robot node. |
| KCF | Faster single-object filter. Full occlusion or a large scale change (ball coming at the camera) drops the target. |
| MOSSE | Hundreds of FPS, weak accuracy. The wrong budget at 15–30 Hz camera rate. |

`BOOSTING`, `MIL`, and `TLD` live under `cv2.legacy` in current OpenCV. Leave them there.

## 2D is cheap. 3D is the contract with locomotion and arms

Options, cheapest to richest:

1. Bearing-only + assumed ball diameter
2. RGB-D (RealSense / Orbbec) if the $15k budget allows one camera
3. Stereo
4. Learned depth

For a rim, a known CAD size plus PnP on detected corners/ellipse is often better than raw depth at range.

## Wrist cameras vs head cameras

Head/ego cameras find things in the room. Wrist cameras make grasps work. GR00T and most manipulation VLAs expect both. Plan mounts and ROS topics now even if you only have a USB webcam and Isaac Sim.

## Success detectors — the CV team's highest-leverage work

RL and evaluation need a boolean (or dense score) that is **not** the policy grading itself. Examples: ball-in-hand, ball-through-rim, object-on-table. These can be tiny models or even classical rules on top of detections. Build them as their own nodes so the RL lead can attach rewards without touching the VLA.

See [basketball skill contracts](06-basketball-task.md) for what those detectors must mean on a real task.
