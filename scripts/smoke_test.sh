#!/usr/bin/env bash
# Builds the workspace, launches the sample talker + listener, and checks that
# messages actually flow. Works natively or inside the Docker image.
set -eo pipefail

WS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$WS"

source /opt/ros/jazzy/setup.bash
echo "==> Building workspace in $WS"
colcon build --symlink-install --event-handlers console_cohesion- >/dev/null
source install/setup.bash

echo "==> Launching talker + listener for 6 s"
LOG="$(mktemp)"
timeout -s INT 6 ros2 launch hello_ros pubsub.launch.py >"$LOG" 2>&1 || true

if grep -q "I heard" "$LOG"; then
  echo "PASS: listener received $(grep -c 'I heard' "$LOG") messages"
  echo "      (ROS 2 Jazzy, rclpy, DDS and colcon are all working)"
  rm -f "$LOG"
else
  echo "FAIL: no messages received. Launch output:"
  cat "$LOG"
  rm -f "$LOG"
  exit 1
fi
