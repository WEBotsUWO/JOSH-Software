# The data pipeline is the product

A VLA is a function from `(images, language, proprioception)` to actions. Fine-tuning is just showing it many aligned examples. If cameras, joints, and the language string are even slightly desynchronized or unlabeled, you will spend months "tuning GR00T" when the bug is the dataset.

[Back to README](../README.md)

## One episode is a row of time, not a folder of pictures

| Field | Source | Notes |
| --- | --- | --- |
| RGB streams | Head, left wrist, right wrist (later: depth) | Constant fps, recorded as video not random PNGs |
| Proprio / state | Joint positions, velocities, gripper, IMU, base pose | Same clock as images. Same joint order forever |
| Actions | What was commanded (teleop or policy) | Relative vs absolute must match GR00T `ActionConfig` |
| Language | Task string + optional subtask | `"put the basketball in the hoop"` and `"grasp the ball"` are different |
| Reward / success | CV success detector + human flag | Store both. Humans override detectors during labeling |
| Meta | Robot id, firmware, camera serials, code git SHA, sim vs real | Without this you cannot debug a bad checkpoint |

## Formats to standardize on

Do not invent a JOSH-only dataset layout.

NVIDIA GR00T fine-tuning expects a GR00T-flavored Hugging Face **LeRobot v2** dataset (`meta/modality.json`, parquet tables, mp4s).

- **Capture format:** ROS 2 bags (or Isaac recorder). Keep bags immutable. Never edit a bag in place.
- **Train format:** LeRobot. The pipeline is the converter plus validators.

### Capture (robot or sim)

rosbag2 or Isaac recorder: images, `/tf`, `/joint_states`, teleop commands, language topic.

### Train (GR00T / LeRobot)

One dataset per embodiment+task mix. Validated modality config. Split train/val **by episode, not by frame** (otherwise the model cheats by seeing the same trajectory).

## Where data comes from this year

| Source | When | What it is good for |
| --- | --- | --- |
| Isaac Sim / Isaac Lab cameras | Fall — now | Unlimited takes, known ground truth, domain randomization |
| Teleop on a cheap arm or mock JOSH | Fall/winter | Real lighting, real cameras, teaches the pipeline before the body exists |
| Human egocentric video | Optional later | GR00T already ate ~20k hours of this (EgoScale). You will not beat that; you fine-tune |
| Synthetic augmentation (Cosmos / DreamGen style) | Winter if compute exists | More lighting/texture variety from a few demos — not a substitute for a correct schema |

This fall you will not have a finished humanoid. That is fine. The first embodiment is Isaac Sim cameras + a fake or partial JOSH. Same schema. Hardware later is another embodiment tag, not a rewrite.

## Quality beats quantity

Ten clean, clock-aligned basketball grasp episodes will out-train 500 desynced ones. Build a validator that rejects episodes with:

- dropped frames
- missing TF
- empty language
- action/state length mismatch

Make that validator a merge gate.

## Annotation is a product too

- **Minimum:** language instruction + success bit
- **Better:** subtask boundaries (`walk`, `grasp`, `shoot`) so you can train skills and stitch them
- **Best:** detector labels on a subset so the success detector can be supervised independently of the VLA
