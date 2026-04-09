#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ROS_WS="${ROS_WS:-$(cd "${REPO_DIR}/../.." && pwd)}"
ROS_DISTRO="${ROS_DISTRO:-jazzy}"

source "/opt/ros/${ROS_DISTRO}/setup.bash"
source "${ROS_WS}/install/setup.bash"

args=()

if [[ -n "${SILVERHAND_ROVER_CAN_IFACE:-}" ]]; then
  args+=("can_iface:=${SILVERHAND_ROVER_CAN_IFACE}")
fi

if [[ -n "${SILVERHAND_ROVER_NODE_ID:-}" ]]; then
  args+=("node_id:=${SILVERHAND_ROVER_NODE_ID}")
fi

if [[ -n "${SILVERHAND_ROVER_QUEUE_LEN:-}" ]]; then
  args+=("queue_len:=${SILVERHAND_ROVER_QUEUE_LEN}")
fi

if [[ -n "${SILVERHAND_ROVER_USE_POWER_BOARD:-}" ]]; then
  args+=("use_power_board:=${SILVERHAND_ROVER_USE_POWER_BOARD}")
fi

if [[ -n "${SILVERHAND_ROVER_POWER_BOARD_CLIENT_NODE_ID:-}" ]]; then
  args+=("power_board_client_node_id:=${SILVERHAND_ROVER_POWER_BOARD_CLIENT_NODE_ID}")
fi

exec ros2 launch silverhand_system_bringup silverhand_system_rover_mock.launch.py "${args[@]}"
