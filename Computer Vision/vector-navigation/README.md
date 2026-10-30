# Vector Navigation

MATLAB visual SLAM on a laptop camera: a sparse map and the camera's poses. A walking direction is a later planner on that map.

[Back to the map](../README.md)

`monovslam` returns 3-D map points and keyframe poses. It does not emit a vector field. Step 6 turns a map into a heading. Footsteps and inverse kinematics stay with locomotion. Monocular scale is not meters until a known object size, a depth camera, or stereo fixes it.

The CV lead owns this order. The folder is specified now. Staffing waits until people move off Vision Training step 1.

## Steps

Finish these before handing a pose and a heading to the RL team.

1. Lock the sensor: a laptop monocular camera. `lidarSLAM` waits until a range sensor exists.
2. Write camera intrinsics (focal lengths, principal point, image size). Label them assumed until a calibration exists.
3. Run `monovslam` on a short image sequence. Save keyframe poses and map points. State in the output note that scale is not metric. The small script is [examples/monocular_vslam.m](examples/monocular_vslam.m).
4. Export pose plus points to a plain file (MAT or CSV) with the frame convention written down.
5. Make a 2D occupancy slice a planner can read. A sparse cloud is not a walkable floor.
6. Desired direction from that map (potential field or vector field histogram). Check the function name in the Navigation Toolbox release you have installed. Output is a heading in the map frame, in the same convention as step 4. Joint angles stay with locomotion.
7. Handoff page for RL: pose, heading, map id, timestamp. Footsteps stay with locomotion.
8. A file drop or ROS 2 bridge only after steps 1–7, at a rate the software lead confirms.

## In this folder

| Path | What it is |
| --- | --- |
| [plan](plan/README.md) | Sensor, toolboxes, and which MATLAB calls are real |
| [structure](structure/README.md) | Pipeline from frames to a heading |
| [examples/monocular_vslam.m](examples/monocular_vslam.m) | Minimal `monovslam` loop on a folder of frames |
| [examples/frames](examples/frames/README.md) | Where that script looks for images |

Requires Computer Vision Toolbox. From R2025a, `monovslam` also runs under Navigation Toolbox when a Computer Vision Toolbox license is present.
