# Vector Navigation structure

[Back to the team list](../README.md)

One camera, an image sequence, then MATLAB. ROS 2 is step 8, after the heading exists.

```mermaid
flowchart LR
  frames[ImageSequence] --> intrinsics[cameraIntrinsics]
  intrinsics --> vslam[monovslam]
  vslam --> points[PointsAndPoses]
  points --> grid[OccupancySlice]
  grid --> heading[Heading]
  heading --> handoff[RLHandoff]
```

## Stage outputs

| Step | Artifact | Frame |
| --- | --- | --- |
| 2 | Intrinsics: focal lengths, principal point, image size `[height width]` | Pixels. Label assumed or calibrated |
| 3 | `mapPoints` as an M-by-3 matrix, `poses` as `rigidtform3d` keyframes | Camera / world as `monovslam` defines them. Scale is not metric |
| 4 | Those arrays in a MAT or CSV, plus a written frame convention | Whatever step 4 freezes. Later stages use that file, not a second convention |
| 5 | 2-D occupancy grid of the floor | The step 4 frame, dropped to the ground plane |
| 6 | One heading in that plane | Same frame as the grid |
| 7 | Pose, heading, map id, timestamp | The step 4 frame, with the timestamp of the pose |

## Handoff fields

Named now so step 7 has a target. Unpublished until steps 1–6 exist.

| Field | Meaning |
| --- | --- |
| `pose` | Camera position and yaw in the step 4 frame. Full `rigidtform3d` if RL asks for it |
| `heading` | Desired direction in the same frame, from step 6 |
| `map_id` | Which export the heading was planned on |
| `timestamp` | When the pose was valid |

Footstep positions and joint angles are not fields on this message.

## Example script

[examples/monocular_vslam.m](examples/monocular_vslam.m) is step 3 in miniature. It reads [examples/frames](examples/frames/README.md), runs `monovslam`, and prints point count and keyframe count. It does not write the MAT file (step 4) and does not compute a heading (step 6).
