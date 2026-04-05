# silverhand_system_bringup

Upper-level system bringup package for Silverhand control, MoveIt, and visualization.

The package keeps MoveIt 2 integration in one place and composes:
- arm model from `silverhand_arm_model`
- arm control from `silverhand_arm_control`
- hand model from `silverhand_hand_model`
- hand control from `silverhand_hand_control`

Current scope:
- planning group for the arm
- separate control of the gripper
- combined arm + hand robot description for MoveIt 2
- split launch modes for `robot` and `gui`

Package:
- `silverhand_system_bringup`

Launch files:
- `silverhand_system_robot.launch.py`
- `silverhand_system_gui.launch.py`
- `silverhand_system_view.launch.py`
- `silverhand_system_mock_rviz.launch.py`
- `silverhand_system_mock.launch.py`
- `silverhand_system_real_rviz.launch.py`
- `silverhand_system_real.launch.py`

## Prerequisites

- Ubuntu `24.04`
- ROS 2 `Jazzy`
- lower/middle layer repositories for the arm and hand packages

Install required ROS packages:

```bash
sudo apt-get update
sudo apt-get install -y \
  ros-jazzy-moveit \
  ros-jazzy-joint-state-publisher \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-ros2-control \
  ros-jazzy-controller-manager \
  ros-jazzy-joint-trajectory-controller \
  ros-jazzy-joint-state-broadcaster \
  ros-jazzy-xacro
```

## Workspace Layout

Recommended layout: build `silverhand_system_bringup` together with the lower-layer arm and hand packages in the same workspace.

```bash
~/silver_ws/src/silverhand_arm_model
~/silver_ws/src/silverhand_arm_control
~/silver_ws/src/silverhand_hand_model
~/silver_ws/src/silverhand_hand_control
~/silver_ws/src/silverhand_system_bringup
```

Optional package if you also keep a combined top-level description:

```bash
~/silver_ws/src/silverhand_system_description
```

## Build

```bash
cd ~/silver_ws
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
```

If the lower-layer packages are built separately, source order must be:

```bash
source /opt/ros/jazzy/setup.bash
source /path/to/lower_layer/install/setup.bash
source /path/to/silverhand_system_bringup/install/setup.bash
```

## Packages Check

```bash
ros2 pkg list | rg silverhand
```

Expected packages:
- `silverhand_arm_model`
- `silverhand_arm_control`
- `silverhand_hand_model`
- `silverhand_hand_control`
- `silverhand_system_bringup`

## Launch

This package supports two deployment styles:
- role-based launch for two physical machines: `robot` and `gui`
- local all-in-one launch for development and smoke tests

Runtime modes:
- `use_mock_hardware:=true` for local testing
- `use_mock_hardware:=false` for real arm and gripper hardware

Viewer only:

```bash
ros2 launch silverhand_system_bringup silverhand_system_view.launch.py
```

Robot machine, role-based launch:

```bash
ros2 launch silverhand_system_bringup silverhand_system_robot.launch.py use_mock_hardware:=true
```

Robot machine with real hardware:

```bash
ros2 launch silverhand_system_bringup silverhand_system_robot.launch.py \
  use_mock_hardware:=false \
  arm_can_iface:=can0 arm_node_id:=100 \
  hand_can_iface:=can0 hand_node_id:=120
```

GUI machine with RViz:

```bash
ros2 launch silverhand_system_bringup silverhand_system_gui.launch.py
```

GUI machine without RViz:

```bash
ros2 launch silverhand_system_bringup silverhand_system_gui.launch.py use_rviz:=false
```

Local all-in-one launch with mock hardware and RViz:

```bash
ros2 launch silverhand_system_bringup silverhand_system_mock_rviz.launch.py
```

Local all-in-one launch with mock hardware, no RViz:

```bash
ros2 launch silverhand_system_bringup silverhand_system_mock.launch.py
```

Local all-in-one launch with real hardware and RViz:

```bash
ros2 launch silverhand_system_bringup silverhand_system_real_rviz.launch.py \
  arm_can_iface:=can0 arm_node_id:=100 \
  hand_can_iface:=can0 hand_node_id:=120
```

Local all-in-one launch with real hardware, no RViz:

```bash
ros2 launch silverhand_system_bringup silverhand_system_real.launch.py \
  arm_can_iface:=can0 arm_node_id:=100 \
  hand_can_iface:=can0 hand_node_id:=120
```

## Notes

- `silverhand_system_bringup` currently composes the arm and gripper into one MoveIt and control bringup with two controllers: `arm_controller` and `hand_controller`.
- `silverhand_system_bringup` depends on the lower-layer arm and gripper packages, especially `silverhand_arm_model`, `silverhand_arm_control`, `silverhand_hand_model`, and `silverhand_hand_control`.
- Planning configuration lives in this package, while hardware access stays in the lower-layer control packages.

## Two-Machine Startup Order

Recommended startup sequence:

1. On the robot computer, launch `silverhand_system_robot.launch.py`.
2. Wait until `move_group` and both controllers are up.
3. On the GUI computer, launch `silverhand_system_gui.launch.py`.
4. Start teleoperation tools after the robot-side nodes are already visible in ROS 2 discovery.

Typical split:
- robot computer: `ros2_control`, `robot_state_publisher`, `move_group`
- gui computer: `rviz2`, teleop UI, operator tools

## WSL And Network Notes

In WSL, `RViz`, `DDS`, `TF`, and planning scene synchronization may produce warnings even when the package itself is configured correctly.

Typical symptoms in WSL:
- RViz starts but does not immediately see the robot state
- `move_group` is running, but the GUI machine discovers topics/actions with delay
- TF or `/joint_states` appear unstable
- intermittent discovery errors between the robot and GUI machines

Because of that:
- treat WSL runs as integration smoke tests, not final network validation
- prefer final bringup and real hardware checks on full Linux machines
- if a launch succeeds in mock mode but RViz still behaves inconsistently, suspect DDS/network timing before suspecting the package layout

## Validation

Useful local checks:

```bash
python3 -m py_compile launch/*.py
source /opt/ros/jazzy/setup.bash
xacro urdf/silverhand_arm_hand.urdf.xacro > /tmp/silverhand_arm_hand.urdf
cd ~/silver_ws
colcon build --packages-select silverhand_system_bringup
```
