# Step 1 - laptop detection stream

[Go to Vision Training](../README.md)

Field meanings live in [Vision Training - Structure](../structure/README.md)

Run the short check first, from `vision-training/`:

```
pip install -r requirements.txt
python examples/webcam_yolo.py
```

Then work in this directory:

```
cd vision-training/step-1
```

## Roles

**Grace**:

| Role | File | Done when |
| --- | --- | --- |
| Camera | [capture.py](capture.py) | Opens camera 0, returns a BGR frame plus a timestamp, raises if the camera fails |
| Detector | [detector.py](detector.py) | Loads `yolo26n.pt` once. Returns class id, class name, confidence, and `xyxy` for one frame. Every class |

### Checklist

- [ ] **Camera**: a window or a print shows a frame and a timestamp.
- [ ] **Detector**: one frame returns a list of boxes from `yolo26n.pt`.

**Valenzia**:

| Role | File | Done when |
| --- | --- | --- |
| Schema | [messages.py](messages.py) | `Detection` and `FrameDetections` round-trip through JSON |
| Rate | [throttle.py](throttle.py) | Passes at most 10 emits per second and counts skips |

### Checklist

- [ ] **Schema**: one `FrameDetections` survives `to_json` and `from_dict` with the same fields.
- [ ] **Rate**: a burst of timestamps yields about 10 allows per second, and `skipped` counts the rest.

**Daniel**:

| Role | File | Done when |
| --- | --- | --- |
| Overlay | [overlay.py](overlay.py) | Draws class, confidence, camera FPS, and emit Hz. Returns the image |
| Logger | [log_writer.py](log_writer.py) | Appends one JSON object per emitted frame to `detections.jsonl` |

### Checklist

- [ ] **Overlay**: one drawn image shows a class name and the two rates.
- [ ] **Logger**: `detections.jsonl` gains one line.

## Notes

- `Logger` pairs with `Schema`
- `Overlay` pairs with `Integrator`
- `Camera` and `Detector` are the two that need a webcam and the weight file (`yolo26n.pt`)
- Integrator: `main` calls the others. The full window can wait if a role is still open.


**Anyone**:

| Role | File | Done when |
| --- | --- | --- |
| Integrator | [run_step1.py](run_step1.py) | Calls the six in that order. Assign this last, or the lead keeps it |

## Final Testing

From this directory:

```
python run_step1.py
```

The webcam opens. Boxes come from `yolo26n.pt`, every class it emits. The window shows camera FPS and emit Hz. `detections.jsonl` grows at about 10 lines per second. `q` quits.

## Scope

Pretrained checkpoint only. Keep every class it outputs. Class filtering is step 3. Tracking is step 4. Weight updates are step 5. ROS 2 is step 7.

Shared names, so the files meet:

| Name | Value |
| --- | --- |
| Weights | `yolo26n.pt` |
| Camera index | `0` |
| Emit rate | `10` Hz |
| Log | `detections.jsonl` in the working directory |
| Quit key | `q` |
