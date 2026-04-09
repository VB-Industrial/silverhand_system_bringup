#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ROS_WS="${ROS_WS:-$(cd "${REPO_DIR}/../.." && pwd)}"
ROS_DISTRO="${ROS_DISTRO:-jazzy}"

source "/opt/ros/${ROS_DISTRO}/setup.bash"
source "${ROS_WS}/install/setup.bash"

exec ros2 launch silverhand_system_bringup silverhand_system_arm_moveit.launch.py \
  use_mock_hardware:="${SILVERHAND_USE_MOCK_HARDWARE:-true}" \
  use_rviz:="${SILVERHAND_USE_RVIZ:-false}"
