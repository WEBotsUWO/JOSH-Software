# Work packages

Size these so one or two developers can own a package for a month without needing the whole brain. The CV lead keeps the interfaces: topic names, dataset schema, action vector, success semantics.

[Back to README](../README.md)

## Active lists

Assign the meeting from the team folders.

- [Vision Training](../vision-training/README.md) — numbered steps. Step 1 is the current assignment.
- [Vector Navigation](../vector-navigation/README.md) — numbered steps. Not staffed this meeting.

The packages below are the older semester map. Use one when a step needs a month-sized owner. Leave the table alone while step 1 is the assignment.

## Packages

| WP | Package | Semester fit | Done when |
| --- | --- | --- | --- |
| 1 | Camera bring-up + ROS 2 image pipeline | Fall week 1–4 | Rectified `Image` + `CameraInfo` in sim and on a USB camera, bagged |
| 2 | Calibration + TF documentation | Fall | Repeatable calibrate procedure; frames named; URDF cameras match bags |
| 3 | Ball + rim detector + ByteTrack | Fall | mAP on a tiny labeled set; overlay topic; track ids stable for 2 seconds |
| 4 | Episode recorder + validator | Fall — **critical path** | Bag → LeRobot converter rejects bad episodes with a readable error |
| 5 | Success detectors (grasp, scored) | Fall/winter | Boolean topics the RL lead can subscribe to; written spec of edge cases |
| 6 | GR00T client + dummy embodiment | Winter | Fake obs in, action chunk out, logged. No need for a full body yet |
| 7 | Fine-tune loop on one skill (grasp ball) | Winter | Checkpoint beats a scripted baseline in Isaac on a fixed scene |
| 8 | Task graph (basketball FSM) | Winter | Sim demo: find → approach → grasp → find hoop → approach → release → success bit |
| 9 | Eval harness + dashboard | Ongoing | N rollouts, success rate, failure tags, video clips of fails |

Fall matches the club roadmap (foundations): WP 1–5, mostly in Isaac. Winter (systems depth): WP 6–8. The roadmap's "full vision system testing" in 2027–28 is hardware on an assembled JOSH. These packages lay the rails.

## Lead vs developers

Developers own a WP. The lead owns naming, clocks, schemas, and the integration tests that prove WP3's tracks are what WP5 and WP8 consume. If two packages can merge without a Slack thread, the interface was written well.

## Interfaces to freeze in week 1 (even as stubs)

- Topic list
- Frame names
- Detection message type
- Episode schema version
- Language string conventions
- Success codes

Changing these later is more expensive than picking an imperfect v0.
