# Humanoid Robot – ROS 2 Jazzy Workspace

Team standard: **ROS 2 Jazzy on Ubuntu 24.04**, everywhere (laptops, lab workstation,
Jetson Orin Nano on JetPack 7.2). Same distro on every machine means a node written
on a laptop runs unchanged on the robot.

```
humanoid_ws/
├── docker/Dockerfile          # shared dev image (Jazzy + team packages)
├── compose.yaml               # works on Windows, Mac and Linux
├── compose.linux.yaml         # Linux extras: host networking, CAN, GUI
├── compose.wsl.yaml           # Windows extras: GUI via WSLg
├── scripts/
│   ├── install_jazzy_native.sh   # native install (Ubuntu 24.04 / Jetson)
│   └── smoke_test.sh             # build + verify everything works
└── src/
    └── hello_ros/             # sample talker/listener package
```

## Pick your setup

| You have | Do this | Good for |
|---|---|---|
| Ubuntu 24.04 (native or dual-boot) | **Option A** | Everything, incl. CAN + Isaac Sim |
| Jetson Orin Nano (JetPack 7.2) | **Option A** with `--base` | The robot |
| Windows or Mac | **Option B** (Docker Desktop) | Learning ROS, path planning, writing nodes |
| Linux, but not 24.04 | **Option B** + Linux override | Most work |

Hardware work (CAN bus, Isaac Sim, talking to the Jetson) needs native Ubuntu 24.04 —
use a lab machine or dual-boot for that.

## Option A – Native install

```bash
git clone <repo-url> ~/humanoid_ws && cd ~/humanoid_ws
bash scripts/install_jazzy_native.sh          # laptop / workstation
bash scripts/install_jazzy_native.sh --base   # Jetson (headless, smaller)
# open a NEW terminal, then:
cd ~/humanoid_ws && bash scripts/smoke_test.sh
```

## Option B – Docker

Install Docker Desktop first. On Windows, use the WSL2 backend and clone the repo
**inside WSL** (e.g. `~/humanoid_ws` in an Ubuntu WSL terminal), not on `C:\` —
builds are far faster.

```bash
git clone <repo-url> ~/humanoid_ws && cd ~/humanoid_ws
docker compose build                  # first time: ~5–10 min
docker compose run --rm smoke-test    # should print PASS
docker compose run --rm dev           # your dev shell
```

The repo is mounted at `~/ws` inside the container, so edit code in VS Code on your
machine and build inside the container. Build artifacts persist between runs.

Extras:
- **Windows GUI (rviz2, rqt):** `docker compose -f compose.yaml -f compose.wsl.yaml run --rm dev`
- **Linux host networking / CAN / GUI:** run `xhost +local:` once, then
  `docker compose -f compose.yaml -f compose.linux.yaml run --rm dev`
- **Linux user isn't UID 1000** (`id -u` to check): put `HOST_UID=<uid>` and
  `HOST_GID=<gid>` in a `.env` file before building.
- **Mac GUI:** not supported in this image; use native Linux for RViz work.

## Day-to-day commands

```bash
cb                                   # (Docker) build + source, alias for:
colcon build --symlink-install && source install/setup.bash

ros2 launch hello_ros pubsub.launch.py rate_hz:=10.0
ros2 run hello_ros talker            # or run nodes individually
ros2 node list | ros2 topic list | ros2 topic echo /chatter | ros2 topic hz /chatter
```

## Cross-machine test (do this once with the Jetson)

Both machines on the same network, same `ROS_DOMAIN_ID` (team default: **42**),
native Ubuntu or Linux Docker with `compose.linux.yaml`:

```bash
# Jetson
ros2 run hello_ros talker
# Laptop
ros2 run hello_ros listener          # should print: I heard "Hello #N from <jetson-hostname>"
```

No messages? University Wi-Fi usually blocks multicast; use a dedicated router or
ethernet switch for the robot network. Also check `printenv | grep ROS` on both.

## Adding your team's package

```bash
cd src
ros2 pkg create --build-type ament_python --license Apache-2.0 <name> --dependencies rclpy
# C++: --build-type ament_cmake --dependencies rclcpp
```

Suggested packages: `humanoid_can_bridge`, `humanoid_perception`, `humanoid_planning`,
`humanoid_control`, `humanoid_interfaces` (custom msgs, ament_cmake).
