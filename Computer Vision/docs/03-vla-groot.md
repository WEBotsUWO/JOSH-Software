# Vision–language–action models

A VLA is a policy with a language handle. It does not "classify then plan then control" as three student-written modules. It maps multimodal tokens to **motor commands**. Classification still exists — inside the vision encoder and VLM — but you rarely read it out unless you add a separate detector.

[Back to README](../README.md)

## Two families

| Family | How actions come out | Examples | Tradeoff |
| --- | --- | --- | --- |
| Monolithic / token VLAs | Discretize each joint into bins; the LLM emits action tokens | RT-2, OpenVLA | Simple; quantization hurts dexterity; LLM rate limits control |
| Dual-system + continuous head | Slow VLM reasons; fast diffusion/flow model emits continuous chunks | π0, GR00T N1.x, CogACT | Better control rate and smoothness; more moving parts to fine-tune |

## What NVIDIA Isaac GR00T actually is

Isaac GR00T is a **platform** (data tools, sim, middleware, Jetson) plus an **open humanoid VLA**. The current public model is **GR00T N1.7** (~3B params).

Lineage: N1 (Mar 2025) → N1.5 → N1.6 → N1.7 (Apr 2026). Fine-tune N1.7. Do not train a new foundation model.

### System 2 — Cosmos-Reason2 2B

Vision-language backbone. Reads RGB (any resolution) + the language instruction. Produces high-level action tokens / embeddings. This is the "understand the command and the scene" half. Runs slower than the motors.

### System 1 — 32-layer DiT

Diffusion transformer. Conditions on System 2 output + live joint state, denoises a **16-step** action chunk. This is the "move the body now" half.

## Inputs and outputs (memorize this)

| Direction | Content |
| --- | --- |
| In | RGB frames + natural language + proprioception (joints, sometimes EEF pose) |
| Out | Continuous action vectors for the embodiment's DoF, typically a 16-step horizon of relative joint motion (grippers often absolute) |

## How this team uses it

1. Freeze a JOSH `NEW_EMBODIMENT` modality config (camera keys, state keys, action keys).
2. Collect LeRobot episodes. See [data pipeline](02-data-pipeline.md).
3. Fine-tune `nvidia/GR00T-N1.7-3B` with `launch_finetune.py`. NVIDIA cites **≥40 GB VRAM** (A100 / L40 / 6000 Ada class). This is a lab-GPU problem, not a laptop problem.
4. Run a policy server and have ROS 2 call `get_action(obs)` in a loop.

Out of the box, N1.7 does not know JOSH's cameras, joint order, or the gym basketball hoop. It also will not give you a calibrated "ball through rim" boolean. That is why [Layer A](01-computer-vision.md) still exists.

EgoScale (tens of thousands of hours of human ego video) is why the **base** model has manipulation priors. JOSH data only has to teach **this body** and **this task**.

## What "general purpose" means in practice

Language lets you reuse one policy for many tasks, but each task still needs demos or a skill library. "Complete any task" is a research slogan.

Operational target for 2026–27: **one language goal that decomposes into skills you can evaluate.** Basketball is a good north star because it forces find → walk → grasp → find → walk → release → verify. See [basketball task](06-basketball-task.md).

## References

- [NVIDIA Isaac GR00T N1.7 blog](https://huggingface.co/blog/nvidia/gr00t-n1-7)
- [NVIDIA/Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T) — start at `getting_started/finetune_new_embodiment.md`
- [OpenVLA paper (2024)](https://arxiv.org/abs/2406.09246) — first 3 pages + architecture figure, so token VLAs make GR00T's DiT head make sense
