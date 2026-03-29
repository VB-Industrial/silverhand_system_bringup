# silverhand_moveit2

Upper-level RViz and MoveIt 2 package for the Silverhand arm.

Package:
- `silverhand_moveit2`

Launch files:
- `silverhand_arm_view.launch.py`
- `silverhand_arm_moveit_mock_rviz.launch.py`
- `silverhand_arm_moveit_mock.launch.py`
- `silverhand_arm_moveit_real_rviz.launch.py`
- `silverhand_arm_moveit_real.launch.py`

## Prerequisites

- Ubuntu `24.04`
- ROS 2 `Jazzy`
- lower/middle layer repository `silverhand_ros2`

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

Recommended layout: build `silverhand_moveit2` and `silverhand_ros2` in the same workspace.

```bash
~/silver_ws/src/silverhand_ros2
~/silver_ws/src/silverhand_moveit2
```

## Build

```bash
cd ~/silver_ws
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
```

If `silverhand_ros2` is built separately, source order must be:

```bash
source /opt/ros/jazzy/setup.bash
source /path/to/silverhand_ros2/install/setup.bash
source /path/to/silverhand_moveit2/install/setup.bash
```

## Packages Check

```bash
ros2 pkg list | rg silverhand
```

Expected packages:
- `silverhand_arm_model`
- `silverhand_arm_control`
- `silverhand_moveit2`

## Launch

Viewer only:

```bash
ros2 launch silverhand_moveit2 silverhand_arm_view.launch.py
```

MoveIt 2 with mock hardware and RViz:

```bash
ros2 launch silverhand_moveit2 silverhand_arm_moveit_mock_rviz.launch.py
```

MoveIt 2 with mock hardware, no RViz:

```bash
ros2 launch silverhand_moveit2 silverhand_arm_moveit_mock.launch.py
```

MoveIt 2 with real hardware and RViz:

```bash
ros2 launch silverhand_moveit2 silverhand_arm_moveit_real_rviz.launch.py can_iface:=can0 node_id:=100
```

MoveIt 2 with real hardware, no RViz:

```bash
ros2 launch silverhand_moveit2 silverhand_arm_moveit_real.launch.py can_iface:=can0 node_id:=100
```

## Notes

- `silverhand_moveit2` depends on the lower-layer arm packages, especially `silverhand_arm_model` and `silverhand_arm_control`.
- In WSL, `RViz`, `DDS` and `TF` warnings may appear because of network and timing issues even when the launch setup is correct.
- Final runtime validation for real hardware is best done on a full Linux machine rather than inside WSL.
