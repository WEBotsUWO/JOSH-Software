#!/usr/bin/env bash
# Native ROS 2 Jazzy install for Ubuntu 24.04 (x86_64 PCs) and the
# Jetson Orin Nano on JetPack 7.2 (arm64, Ubuntu 24.04).
#
#   bash scripts/install_jazzy_native.sh            # desktop (rviz2, rqt, demos)
#   bash scripts/install_jazzy_native.sh --base     # headless; use on the Jetson
set -euo pipefail

VARIANT="desktop"
[[ "${1:-}" == "--base" ]] && VARIANT="ros-base"

. /etc/os-release
if [[ "${VERSION_CODENAME}" != "noble" ]]; then
  echo "ERROR: Jazzy needs Ubuntu 24.04 (noble); this is ${PRETTY_NAME}." >&2
  if [[ -f /etc/nv_tegra_release ]]; then
    echo "This Jetson is on an older JetPack. Reflash it to JetPack 7.2 first." >&2
  fi
  exit 1
fi

echo "==> Locale"
sudo apt-get update
sudo apt-get install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

echo "==> ROS 2 apt source"
sudo apt-get install -y software-properties-common curl
sudo add-apt-repository -y universe
ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest \
  | grep -F '"tag_name"' | awk -F'"' '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb \
  "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.${VERSION_CODENAME}_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

echo "==> Installing ros-jazzy-${VARIANT} + team packages"
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y \
  "ros-jazzy-${VARIANT}" ros-dev-tools \
  python3-colcon-common-extensions \
  can-utils python3-can \
  ros-jazzy-ros2-control ros-jazzy-ros2-controllers \
  ros-jazzy-rmw-cyclonedds-cpp

echo "==> rosdep"
[[ -f /etc/ros/rosdep/sources.list.d/20-default.list ]] || sudo rosdep init
rosdep update --rosdistro jazzy

echo "==> Shell setup"
grep -qxF 'source /opt/ros/jazzy/setup.bash' ~/.bashrc || \
  echo 'source /opt/ros/jazzy/setup.bash' >> ~/.bashrc
grep -qF 'ROS_DOMAIN_ID' ~/.bashrc || \
  echo 'export ROS_DOMAIN_ID=42   # whole team uses the same ID' >> ~/.bashrc

echo
echo "Done. Open a new terminal, then from the repo root run:"
echo "  colcon build --symlink-install && source install/setup.bash"
echo "  bash scripts/smoke_test.sh"
