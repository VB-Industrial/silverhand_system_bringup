# silverhand_system_bringup

Upper-level bringup package for SilverHand orchestration.

Каноническая сущностная модель:

- `arm`
- `arm_hand`
- `rover`
- `system = rover + arm + hand`

Режимы:

- `arm`: `mock`, `ros_control`, `moveit`
- `arm_hand`: `mock`, `ros_control`, `moveit`
- `rover`: `mock`, `ros_control`
- `system`: `mock`, `ros_control`, `moveit`

`silverhand_system_bringup` теперь оркестрирует запуск. Источник правды для hardware transport defaults лежит в нижних пакетах:

- [silverhand_arm_control/config/hardware_profiles.yaml](/home/r/silver_ws/src/silverhand_arm_control/config/hardware_profiles.yaml)
- [silverhand_hand_control/config/hardware_profiles.yaml](/home/r/silver_ws/src/silverhand_hand_control/config/hardware_profiles.yaml)
- [silverhand_rover_control/config/hardware_profiles.yaml](/home/r/silver_ws/src/silverhand_rover_control/config/hardware_profiles.yaml)

## What This Package Owns

- arm-only MoveIt orchestration
- arm+hand MoveIt orchestration
- full-system rover+arm+hand orchestration
- GUI entrypoints
- RViz-only viewer

## Dependencies

- Ubuntu 24.04
- ROS 2 Jazzy

Минимально:

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

Ожидаемый layout:

```bash
~/silver_ws/src/silverhand_arm_model
~/silver_ws/src/silverhand_arm_control
~/silver_ws/src/silverhand_hand_model
~/silver_ws/src/silverhand_hand_control
~/silver_ws/src/silverhand_rover_model
~/silver_ws/src/silverhand_rover_control
~/silver_ws/src/silverhand_system_bringup
```

Опционально:

```bash
~/silver_ws/src/silverhand_rover_teleop
~/silver_ws/src/silverhand_system_description
```

## Build

```bash
cd ~/silver_ws
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
```

## Canonical Launch Files

### Arm

```bash
ros2 launch silverhand_system_bringup silverhand_system_arm_mock.launch.py
ros2 launch silverhand_system_bringup silverhand_system_arm_ros_control.launch.py
ros2 launch silverhand_system_bringup silverhand_system_arm_moveit.launch.py use_mock_hardware:=true use_rviz:=false
```

### Arm + Hand

```bash
ros2 launch silverhand_system_bringup silverhand_system_arm_hand_mock.launch.py
ros2 launch silverhand_system_bringup silverhand_system_arm_hand_ros_control.launch.py
ros2 launch silverhand_system_bringup silverhand_system_arm_hand_moveit.launch.py use_mock_hardware:=true use_rviz:=false
```

### Rover

```bash
ros2 launch silverhand_system_bringup silverhand_system_rover_mock.launch.py
ros2 launch silverhand_system_bringup silverhand_system_rover_ros_control.launch.py
```

Low-level passthrough:

```bash
ros2 launch silverhand_system_bringup silverhand_system_rover.launch.py
```

`silverhand_system_rover.launch.py` просто включает upstream [silverhand_rover_bringup.launch.py](/home/r/silver_ws/src/silverhand_rover_control/launch/silverhand_rover_bringup.launch.py). Значения по умолчанию для rover transport и IMU задаются в `silverhand_rover_control`.

### Full System

Mock:

```bash
ros2 launch silverhand_system_bringup silverhand_system_mock.launch.py
```

ros2_control:

```bash
ros2 launch silverhand_system_bringup silverhand_system_ros_control.launch.py
```

MoveIt:

```bash
ros2 launch silverhand_system_bringup silverhand_system_moveit.launch.py use_mock_hardware:=true use_rviz:=false
```

Full-system launch использует:

- rover как root `base_link`
- arm links с префиксом `arm_`
- arm joints без префикса `joint_1..joint_6`
- hand joints `hand_left_finger_joint` и `hand_right_finger_joint`

Это позволяет держать совместимость с существующими arm controllers и MoveIt-конфигом, но убрать конфликт `base_link` между rover и arm.

## GUI And Visualization

Arm GUI:

```bash
ros2 launch silverhand_system_bringup silverhand_system_gui_arm.launch.py
```

Rover GUI:

```bash
ros2 launch silverhand_system_bringup silverhand_system_gui_rover.launch.py
```

RViz-only viewer:

```bash
ros2 launch silverhand_system_bringup silverhand_system_view_only_rviz.launch.py
```

Role-based arm+hand MoveIt without RViz:

```bash
ros2 launch silverhand_system_bringup silverhand_system_arm_hand_robot.launch.py use_mock_hardware:=true
```

## Helper Scripts

Канонические scripts:

```bash
./scripts/start_system_mock.sh
./scripts/start_system_ros_control.sh
./scripts/start_system_moveit.sh
./scripts/start_system_arm_mock.sh
./scripts/start_system_arm_ros_control.sh
./scripts/start_system_arm_moveit.sh
./scripts/start_system_arm_hand_mock.sh
./scripts/start_system_arm_hand_ros_control.sh
./scripts/start_system_arm_hand_moveit.sh
./scripts/start_system_rover_mock.sh
./scripts/start_system_rover_ros_control.sh
./scripts/start_system_gui_arm.sh
./scripts/start_system_gui_rover.sh
./scripts/start_system_view_only_rviz.sh
```

Role-based convenience script:

```bash
./scripts/start_system_arm_hand_robot.sh
```

## Environment Variables

Общие:

- `ROS_WS`
- `ROS_DISTRO`
- `SILVERHAND_USE_RVIZ`
- `SILVERHAND_USE_MOCK_HARDWARE`

Rover overrides:

- `SILVERHAND_ROVER_CAN_IFACE`
- `SILVERHAND_ROVER_NODE_ID`
- `SILVERHAND_ROVER_QUEUE_LEN`
- `SILVERHAND_ROVER_USE_IMU_ODOMETRY`
- `SILVERHAND_ROVER_USE_POWER_BOARD`
- `SILVERHAND_ROVER_POWER_BOARD_CLIENT_NODE_ID`

Rover GUI:

- `SILVERHAND_ROVER_GUI_HOST`
- `SILVERHAND_ROVER_GUI_PORT`

Важно:

- arm/hand transport defaults больше не задаются в `silverhand_system_bringup`
- system-level rover overrides здесь только переопределяют defaults из `silverhand_rover_control`, но не заменяют источник правды

## systemd

User service template:

- [silverhand-system-bringup@.service](/home/r/silver_ws/src/silverhand_system_bringup/systemd/user/silverhand-system-bringup@.service)

Канонические instance names:

```bash
systemctl --user start silverhand-system-bringup@mock
systemctl --user start silverhand-system-bringup@ros_control
systemctl --user start silverhand-system-bringup@moveit
systemctl --user start silverhand-system-bringup@arm_mock
systemctl --user start silverhand-system-bringup@arm_ros_control
systemctl --user start silverhand-system-bringup@arm_moveit
systemctl --user start silverhand-system-bringup@arm_hand_mock
systemctl --user start silverhand-system-bringup@arm_hand_ros_control
systemctl --user start silverhand-system-bringup@arm_hand_moveit
systemctl --user start silverhand-system-bringup@rover_mock
systemctl --user start silverhand-system-bringup@rover_ros_control
systemctl --user start silverhand-system-bringup@gui_arm
systemctl --user start silverhand-system-bringup@gui_rover
systemctl --user start silverhand-system-bringup@view_only_rviz
```

Role-based instance:

```bash
systemctl --user start silverhand-system-bringup@arm_hand_robot
```

## Implementation Notes

Full-system URDF:

- [silverhand_system.urdf.xacro](/home/r/silver_ws/src/silverhand_system_bringup/urdf/silverhand_system.urdf.xacro)

Full-system launch core:

- [silverhand_system_full_common.launch.py](/home/r/silver_ws/src/silverhand_system_bringup/launch/silverhand_system_full_common.launch.py)

Full-system SRDF:

- [system.srdf](/home/r/silver_ws/src/silverhand_system_bringup/config/system.srdf)

## Verified

Проверено:

- `python3 -m py_compile launch/*.launch.py`
- `bash -n scripts/*.sh`
- `colcon build --packages-select silverhand_arm_model silverhand_system_bringup`
- `xacro` для full-system URDF разворачивается с rover `base_link`, arm links `arm_*` и arm joints `joint_1..joint_6`
- `ros2 launch ... --show-args` для
  - `silverhand_system_mock.launch.py`
  - `silverhand_system_ros_control.launch.py`
  - `silverhand_system_moveit.launch.py`
