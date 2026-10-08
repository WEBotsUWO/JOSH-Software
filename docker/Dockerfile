# Shared ROS 2 Jazzy dev image for the humanoid project.
# Multi-arch: builds on x86_64 laptops/workstations and arm64 (Apple Silicon, Jetson).
FROM osrf/ros:jazzy-desktop

ARG USERNAME=ros
ARG USER_UID=1000
ARG USER_GID=1000
ENV DEBIAN_FRONTEND=noninteractive

# Ubuntu 24.04 images ship a default "ubuntu" user on UID 1000 - remove it so our
# user can take that UID and files in the bind-mounted repo stay owned by you.
RUN userdel -r ubuntu 2>/dev/null || true \
 && groupadd --gid ${USER_GID} ${USERNAME} \
 && useradd --uid ${USER_UID} --gid ${USER_GID} -m -s /bin/bash ${USERNAME} \
 && apt-get update && apt-get install -y --no-install-recommends sudo \
 && echo "${USERNAME} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
 && chmod 0440 /etc/sudoers.d/${USERNAME} \
 && rm -rf /var/lib/apt/lists/*

# Dev tools + what the sub-teams need on day one.
#   can-utils / python3-can : ROS bridge team (CAN telemetry)
#   ros2-control            : low/mid-level control tiers
#   rmw-cyclonedds          : alternative middleware if Fast DDS discovery misbehaves
RUN apt-get update && apt-get install -y --no-install-recommends \
      git vim nano less bash-completion iputils-ping iproute2 \
      python3-pip python3-colcon-common-extensions python3-rosdep \
      can-utils python3-can \
      ros-jazzy-ros2-control ros-jazzy-ros2-controllers \
      ros-jazzy-rmw-cyclonedds-cpp \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages --ignore-installed -r /tmp/requirements.txt

USER ${USERNAME}
WORKDIR /home/${USERNAME}/ws

RUN rosdep update --rosdistro jazzy \
 && echo 'source /opt/ros/jazzy/setup.bash' >> ~/.bashrc \
 && echo '[ -f ~/ws/install/setup.bash ] && source ~/ws/install/setup.bash' >> ~/.bashrc \
 && echo 'source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash 2>/dev/null' >> ~/.bashrc \
 && echo 'alias cb="cd ~/ws && colcon build --symlink-install && source install/setup.bash"' >> ~/.bashrc

CMD ["bash"]
