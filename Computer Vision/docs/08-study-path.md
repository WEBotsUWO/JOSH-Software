# Study path

Do not start at GR00T GitHub issues. Start at cameras and MDPs, then climb. Depth over folklore.

[Back to README](../README.md)

## Start here

| Item | Why |
| --- | --- |
| ROS 2 mental model: nodes, topics, TF, bags | Every CV artifact lives here |
| Pinhole camera + calibration (any 20-minute explainer + OpenCV `calibrateCamera` docs) | Otherwise 3D is mysticism |
| Ultralytics YOLO26, checkpoint `yolo26n.pt` | Vision Training's first model. [Steps](../vision-training/README.md) |
| MathWorks `monovslam` (Computer Vision Toolbox) | Vector Navigation's first model. Navigation Toolbox is the later heading planner. [Steps](../vector-navigation/README.md) |
| Silver L1–L2 | Shared language with the RL lead |
| Hugging Face GR00T N1.7 blog + Isaac GR00T inputs/outputs FAQ | Know the actual I/O, not the marketing |
| LeRobot dataset page (v2 layout) | You will live in this format |

Then ship a detector and a validator in sim. The laptop slice of that detector is [Vision Training step 1](../vision-training/README.md): pretrained YOLO26n, a detection record, 10 Hz. Reading GR00T issues before you have `/image_raw` and a schema is how the team gets lost.

## Fall 2026 — foundations

Club roadmap: RL, sim, CAD, CAN, motors. For CV that translates to: sim cameras in Isaac, detector baseline, dataset schema, **no foundation-model training**. Mechanical will not give you a torso yet; do not block on it.

## Winter 2026 — systems depth

Club roadmap: deep learning and better integration. That is GR00T fine-tune on one skill, success detectors hooked to RL, task graph in sim. "Vision system testing" on the 2027–28 card is full-body hardware — you are laying the rails now.

## Canonical reading (small set)

| Resource | Use |
| --- | --- |
| [David Silver RL course](https://davidstarsilver.wordpress.com/teaching/) | Theory interface with the RL lead |
| [NVIDIA Isaac GR00T N1.7 blog](https://huggingface.co/blog/nvidia/gr00t-n1-7) | Dual-system VLA, EgoScale, fine-tune |
| [Ultralytics docs](https://docs.ultralytics.com/) | YOLO26 load, predict, and later track. Vision Training |
| [monovslam](https://www.mathworks.com/help/vision/ref/monovslam.html) | MATLAB monocular SLAM. Vector Navigation step 3 |
| [Navigation Toolbox](https://www.mathworks.com/help/nav/index.html) | Occupancy maps and heading planners after the SLAM map exists |
| [NVIDIA/Isaac-GR00T `finetune_new_embodiment.md`](https://github.com/NVIDIA/Isaac-GR00T/blob/main/getting_started/finetune_new_embodiment.md) | The file WP6/WP7 will follow |
| [OpenVLA paper (2024)](https://arxiv.org/abs/2406.09246) — first 3 pages + architecture figure | Understand token VLAs so GR00T's DiT head makes sense |
| Isaac Lab + Isaac Sim camera tutorials | Fall playground |

Next after this map: a tldraw diagram plus one page per work package written so a new developer can start without Slack lore. Do not draw that until this map matches what is in people's heads.
