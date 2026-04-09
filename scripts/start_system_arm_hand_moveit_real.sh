#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ROS_WS="${ROS_WS:-$(cd "${REPO_DIR}/../.." && pwd)}"
ROS_DISTRO="${ROS_DISTRO:-jazzy}"

source "/opt/ros/${ROS_DISTRO}/setup.bash"
source "${ROS_WS}/install/setup.bash"

echo "DEPRECATED: start_system_arm_hand_moveit_real.sh is a legacy alias. Use start_system_arm_hand_moveit.sh." >&2
export SILVERHAND_USE_MOCK_HARDWARE="${SILVERHAND_USE_MOCK_HARDWARE:-false}"
exec "${SCRIPT_DIR}/start_system_arm_hand_moveit.sh"
