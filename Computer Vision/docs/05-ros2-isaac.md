# ROS 2, Isaac, and where Python actually runs

Python is the research language. ROS 2 is the nervous system. Isaac is the gym and the pretrained brain. Mixing them without a diagram is how student teams lose a semester.

[Back to README](../README.md)

## ROS 2 — what CV nodes look like

| Node / topic family | Job |
| --- | --- |
| camera drivers + `camera_info` | Publish `Image` + `CameraInfo`. Never drop `CameraInfo`. |
| `image_proc` / rectify (optional) | Undistort if detectors need it. Record both raw and rectified? Pick one and document. |
| detector nodes | Subscribe `Image`, publish `vision_msgs/Detection2DArray` (or equivalent) at the 10 Hz target, plus a debug `Image` overlay |
| tracker (ByteTrack) | Detections in, tracks with stable ids out. SORT only if this node misses detector rate |
| `success_detector` | Tracks + optional depth → `/task/success`, `/task/reward` |
| `gr00t_client` | Assemble obs dict from images + joints + language, call policy server, publish action chunk |
| rosbag2 | Record the contract topics. This is how datasets are born |

Use `tf2` for every 3D quantity. Use message filters to associate camera and joints. Decide QoS (sensor data vs reliable) once and write it down.

## The NVIDIA pile, decoded

| Name | Role for JOSH |
| --- | --- |
| Isaac Sim | The 3D world. Cameras, lights, basketball, hoop, robot URDF. Where you debug vision without hardware |
| Isaac Lab | RL / imitation training at scale on top of Sim. RL team's main gym |
| Isaac GR00T (model) | The VLA checkpoint you fine-tune |
| Isaac GR00T (platform) | Teleop, data, whole-body control helpers, deployment scripts |
| Cosmos | World/reasoning models and synthetic video. Useful later; do not block fall on it |
| Jetson (Orin / Thor) | On-robot inference. Thor is the GR00T marketing target. A $15k robot may infer on a nearby workstation first |

## Budget reality

Full-size humanoids and Jetson AGX Thor are usually more than the $15k target by themselves. Design the software as if cameras + a sim robot are the first embodiment, with a modality config that can add joints later. That is how GR00T expects new embodiments to work.

## Control loop frequencies (order of magnitude)

| Loop | Rate |
| --- | --- |
| Cameras | 15–30 Hz |
| Detector publish | 10 Hz until the software lead confirms a different number. Cameras may be faster; throttle the publish |
| VLM System 2 | ~5–10 Hz |
| Action DiT chunks | Designed so the low-level controller can run faster than the VLM |
| Motor PID | Hundreds of Hz on embedded (not CV) |

The ROS graph must not assume everything runs at 30 Hz.

MATLAB visual SLAM ([Vector Navigation](../vector-navigation/README.md)) runs in MATLAB on image sequences. It is an offline dev track. A ROS 2 bridge is the last step on that list, after the map and the heading exist.
