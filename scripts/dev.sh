#!/usr/bin/env bash
# Open a ROS shell. First terminal starts the container; later terminals join it.
cd "$(dirname "$0")/.."
if docker ps --format '{{.Names}}' | grep -qx ros2-dev; then
  exec docker exec -it ros2-dev bash
fi
FILES="-f compose.yaml"
grep -qi microsoft /proc/version 2>/dev/null && FILES="$FILES -f compose.wsl.yaml"   # Windows GUI
exec docker compose $FILES run --rm --name ros2-dev dev
