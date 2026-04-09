#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ROS_WS="${ROS_WS:-$(cd "${REPO_DIR}/../.." && pwd)}"
ROS_DISTRO="${ROS_DISTRO:-jazzy}"

set +u
source "/opt/ros/${ROS_DISTRO}/setup.bash"
source "${ROS_WS}/install/setup.bash"
set -u

exec ros2 launch silverhand_system_bringup silverhand_system_gui_rover.launch.py \
  ros_ws:="${ROS_WS}" \
  host:="${SILVERHAND_ROVER_GUI_HOST:-0.0.0.0}" \
  port:="${SILVERHAND_ROVER_GUI_PORT:-4174}"
