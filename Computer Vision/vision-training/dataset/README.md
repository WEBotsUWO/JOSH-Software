# Dataset and fine-tune

[Go to Vision Training](../README.md)

The classes we need to identify: [classes.yaml](../classes.yaml) (2026 names)

## What we train on

EgoObjects (Meta, ICCV 2023). Wearable cameras in homes and offices, so the view is eye level or lower, with 2D boxes. The public image zip is about 37 GiB. This folder reads a prefix of that zip and stops at 9 GB, then keeps the JPEGs that belong to train or val.

Annotation JSON is about 0.24 GB on top of that, so the download stays under 10 GB. The zip is stored with a size in each local header, which is why a prefix still decompresses. Rerun the same command to resume.

The files come from the Hugging Face copy `Myszz/EgoObjects`. Two of them are named backwards from the split written inside:

| File | What is inside |
| --- | --- |
| `Meta_EgoObjects_Test.json` | Train images. No `subset` field. |
| `Meta_EgoObjects_Train.json` | `subset: val` and `subset: test`. |

The scripts follow `subset`. A missing subset is train. `test` is never written into the YOLO set.

## What we do not use

RoboSense is 705 GB of outdoor footage. Its boxes are vehicle, pedestrian, and cyclist. The 10 GB `part_*` files are pieces of one tar, so one part does not open. It does not cover this class list.

## Model

Fine-tune `yolo26n.pt`. That is the same checkpoint step 1 already runs. Training starts from those weights and writes `runs/josh-ego`. It does not replace `yolo26n.pt`.

The fine-tune head only contains must-list classes that have boxes in the slice. EgoObjects has no people. `person` and `bed` stay on `yolo26n`. `rim`, `backboard`, `basketball net`, `fire extinguisher`, and `cable` have no boxes here. [prompt_classes.py](prompt_classes.py) asks YOLOE-26n for the whole list by text, which is the open-vocabulary step until those photos exist.

## dataset/raw

`dataset/raw/` is gitignored. Nothing in it is committed. From `vision-training`, with the venv, each developer creates it the same way:

```
python dataset/download_subset.py
```

The script makes the folder and fills it:

| Path | What it is |
| --- | --- |
| `Meta_EgoObjects_Val.json` | Category names |
| `Meta_EgoObjects_Test.json` | Train images and boxes |
| `Meta_EgoObjects_Train.json` | Val and test images and boxes |
| `images/` | JPEGs from the front of the zip |
| `download_state.json` | Where to resume |

Do not copy `raw/` between machines. Run the command again. It skips files that are already the right size and continues the zip from `download_state.json`.

## Run

From `vision-training`, with the venv:

```
python dataset/download_subset.py
python dataset/prepare_yolo.py
python dataset/train.py --device 0
```

`download_subset.py` defaults to `--max-gb 9`. The zip is sorted by file name, so the first few dozen megabytes are one video and the 9 GB default is a few hundred. Run `prepare_yolo.py` after that download stops. It writes `dataset/yolo` and `coverage.json` (which must-list names made it into the head). `train.py` is the GPU job. `--device 0` is the first GPU on the machine you SSH to.

To print the 2026 names without a model:

```
python dataset/prompt_classes.py --list
```

To run YOLOE-26n on one photo:

```
python dataset/prompt_classes.py --image path\to\photo.jpg
```

## Citations

EgoObjects: Chenchen Zhu et al., "EgoObjects: A Large-Scale Egocentric Dataset for Fine-Grained Object Understanding", ICCV 2023. [GitHub](https://github.com/facebookresearch/EgoObjects)
