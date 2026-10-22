# Worked example: mini basketball

This is a long-horizon task. Treating it as one VLA rollout is how you get a robot that wanders. Treat it as a **task graph** whose nodes have CV preconditions and success detectors.

[Back to README](../README.md)

```mermaid
flowchart LR
  findBall[Find ball] --> walkBall[Walk to ball]
  walkBall --> grasp[Pick it up]
  grasp --> findHoop[Find hoop]
  findHoop --> walkHoop[Walk to shooting pose]
  walkHoop --> shoot[Lift, aim, release]
  shoot --> confirm[Confirm the score]
```

Not a single pipeline from "CNN" to "motors." A horizontal task graph, and a vertical stack (cameras → perception → dataset → VLA/RL → control) that every node of the graph reuses.

## Who does what

| Slice | Owner | Basketball job |
| --- | --- | --- |
| Find ball / rim | CV — detection pair | Two classes, one ByteTrack, debug overlays |
| Walk toward target | RL locomotion + CV target | CV publishes a frame+point; walking policy consumes it |
| Grasp / shoot chunks | VLA fine-tune | Teleop demos in sim (then real). Wrist cameras matter |
| Sequencer | CV lead + software lead | Finite state machine or behavior tree calling skills |
| Score / terminate | CV success detector | The only thing allowed to say the task is done |

## Skill contracts

### 1. Find the ball

- **Computer vision:** The live model starts as pretrained YOLO26n, many classes, from [Vision Training](../vision-training/README.md). Ball and rim weights are step 5 of that list, after the pretrained stream works. Output a 2D box, class, confidence, and, once step 4 lands, a stable track id.
- **VLA / policy:** The instruction "pick up the basketball" already biases GR00T toward ball-like objects. Detection is still required so you can score success and debug misses.
- **Success:** A track exists for ≥ N frames with confidence above threshold, and the ball is in the reachable workspace estimate.
- **Likely failures:** Occlusion, similar orange objects, motion blur while walking, camera exposure blowout on gym lights.

### 2. Walk to the ball

- **Computer vision:** Keep the track alive. Estimate bearing and rough range (depth camera, stereo, or monocular size prior). Publish a **navigation target**, not raw pixels.
- **VLA / policy:** A whole-body VLA can output walking + gaze together. On JOSH year one, locomotion is more likely an RL policy; CV only supplies the target.
- **Success:** Ball stays in view or is reacquired. Robot base is within grasp radius. Collision-free path.
- **Likely failures:** Looking at the floor loses the hoop later; looking at the hoop loses the ball. Need a gaze / memory policy.

### 3. Pick it up

- **Computer vision:** Hand-object overlap, grip width vs ball diameter, whether the ball rose with the hand after close. Wrist cameras help more than the head camera here.
- **VLA / policy:** This is the skill GR00T is actually good at after fine-tuning: short-horizon dexterous chunks conditioned on wrist + ego RGB and gripper state.
- **Success:** Ball centroid follows the wrist for K consecutive frames after gripper close. Optional: contact / current spike from electrical.
- **Likely failures:** False grasp (fingers closed on air). Ball squeezed out. Wrong object grasped.

### 4. Find the hoop

- **Computer vision:** Detect backboard / rim as a **separate class** from the ball. Estimate rim center in 3D. Do not reuse the ball detector.
- **VLA / policy:** Language can switch the goal ("walk to the hoop") but the verifier still needs an explicit rim pose to know if alignment is good.
- **Success:** Rim detected with a stable 3D estimate. Ball still in hand (grasp success must remain true).
- **Likely failures:** Gym clutter, other hoops, rim too small at distance, overexposed windows behind the backboard.

### 5. Walk to shooting pose

- **Computer vision:** Track rim. Compute a shooting stance (distance, heading, torso facing). Warn if the ball track is lost while walking.
- **VLA / policy:** Long-horizon; better as a task graph than one 20-second VLA rollout. VLA handles local foot/arm adjustment near the stance.
- **Success:** Robot inside a shooting annulus in front of the rim, facing it, ball still grasped.
- **Likely failures:** Walking into the post. Stance too close/far. Dropping the ball mid-walk.

### 6. Lift, aim, release

- **Computer vision:** Wrist + ego views of rim. At release, start a "ball in flight" track. Do not require the VLA to also run the score detector.
- **VLA / policy:** Short action chunk: lift, extend, open gripper. Fine-tuned on teleop of this exact skill.
- **Success:** Gripper open AND ball separated from hand AND ball moving toward rim (optional trajectory).
- **Likely failures:** Under-release. Ball stuck. Arms collide with torso. Timing mismatch with locomotion sway.

### 7. Confirm the score

- **Computer vision:** This is a success detector, not a VLA. Ball passes through rim plane downward, or lands in a net ROI, then is no longer in hand.
- **VLA / policy:** If the VLA is used for recovery ("pick up the missed ball"), confirmation is still an external reward / terminate signal.
- **Success:** Task graph emits `SUCCEEDED`. Episode is labeled and stored. Counter-example: ball bounced off rim.
- **Likely failures:** Celebrating a miss. Never terminating. Reward hacking on "ball near hoop" instead of through the rim.
