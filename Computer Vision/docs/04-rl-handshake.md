# How CV talks to reinforcement learning

The software lead's David Silver lectures are the right theory. CV does not need to implement PPO. CV does need to know what an MDP looks like on JOSH, because **observation** and **reward** are mostly CV problems.

[Back to README](../README.md)

## MDP interface

| MDP piece | On JOSH | CV lead owns? |
| --- | --- | --- |
| State / observation | Images, detections, tracks, estimated poses, joint state | Yes — define and document the observation dict |
| Action | Joint targets / whole-body commands | Shared contract with controls; not motor tuning |
| Transition | Physics in Isaac Lab, or the real robot | Simulation team; CV owns sim cameras looking realistic enough |
| Reward | +1 ball through rim; shaping for distance-to-ball, grasp, facing hoop | Yes — success detectors + documented shaping |
| Policy | RL locomotion, or RL fine-tune of the VLA action head | RL team; CV supplies obs/reward and eval videos |

You should be able to draw JOSH basketball as an MDP on a whiteboard with the RL lead in one sitting.

## What this team hands the RL team

Two messages, on different schedules. Joint targets stay in the Action row above.

| From | Payload | Rate |
| --- | --- | --- |
| [Vision Training](../vision-training/README.md) | Detection record: class id, name, confidence, `xyxy`, frame time, emit time. Track id once ByteTrack is in (step 4) | 10 Hz until the software lead confirms a different number |
| [Vector Navigation](../vector-navigation/README.md) | Pose, desired heading, map id, timestamp | Unpublished until that folder's steps 1–7 exist. Rate confirmed with the same lead |

Locomotion turns a heading into footsteps. Arms turn a box into a grasp.

## Three different RL jobs (do not mash them)

### Locomotion in sim

Isaac Lab trains walking/balancing with privileged state, then you may distill to vision. CV enters if the policy must walk toward a **seen** object.

### Skill fine-tune

Start from teleop/VLA imitation, then RL to improve grasp success. Needs a dense or at least unbiased grasp reward from cameras.

### Task-level

Sparse +1 when the hoop success detector fires. Too sparse without a task graph. Usually hierarchical: RL/VLA skills + a scripted or learned sequencer.

## Reward hacking is a CV bug

If you reward "ball near orange circle," the policy will stand next to the hoop holding the ball and collect reward. The detector must encode the real task: **through the rim, downward, after a release, not in-hand.**

## What to read from Silver

- Lecture 1 — what RL is
- Lecture 2 — MDPs (this is the interface document)
- Lectures 6–7 — why we use function approximation and policy gradients on robots

Skip games (L10) until you care.

Course: [https://davidstarsilver.wordpress.com/teaching/](https://davidstarsilver.wordpress.com/teaching/)
