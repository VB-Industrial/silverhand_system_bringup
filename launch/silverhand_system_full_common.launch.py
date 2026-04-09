from pathlib import Path
import copy
import os
import tempfile
import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, OpaqueFunction
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def load_file(package_name, relative_path):
    package_path = get_package_share_directory(package_name)
    absolute_path = os.path.join(package_path, relative_path)
    with open(absolute_path, "r", encoding="utf-8") as file:
        return file.read()


def load_yaml(package_name, relative_path):
    package_path = get_package_share_directory(package_name)
    absolute_path = os.path.join(package_path, relative_path)
    with open(absolute_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_profile(package_name, profile_name):
    profiles = load_yaml(package_name, "config/hardware_profiles.yaml")["profiles"]
    return profiles[profile_name]


def _is_truthy(value: str) -> bool:
    return value.lower() in ("true", "1", "yes", "on")


def _resolve_override(value: str, fallback) -> str:
    return value if value != "" else str(fallback)


def _detect_imu_available(imu_device_path: str, imu_vid: str, imu_pid: str) -> bool:
    if imu_device_path:
        return Path(imu_device_path).exists()

    try:
        vid_hex = f"{int(imu_vid):04x}"
        pid_hex = f"{int(imu_pid):04x}"
    except ValueError:
        return False

    for hidraw_dir in Path("/sys/class/hidraw").glob("hidraw*"):
        uevent_file = hidraw_dir / "device" / "uevent"
        if not uevent_file.exists():
            continue

        try:
            contents = uevent_file.read_text()
        except OSError:
            continue

        expected_fragment = f"HID_ID=0003:{vid_hex.upper()}:{pid_hex.upper()}"
        if expected_fragment in contents.upper():
            return True

    return False


def create_runtime_nodes(context):
    use_rviz = LaunchConfiguration("use_rviz").perform(context)
    run_system_bringup = LaunchConfiguration("run_system_bringup").perform(context)
    run_move_group = LaunchConfiguration("run_move_group").perform(context)
    use_mock_hardware = LaunchConfiguration("use_mock_hardware").perform(context)
    rviz_config = LaunchConfiguration("rviz_config").perform(context)

    profile_name = "mock" if _is_truthy(use_mock_hardware) else "ros_control"
    rover_profile = load_profile("silverhand_rover_control", profile_name)
    arm_profile = load_profile("silverhand_arm_control", profile_name)
    hand_profile = load_profile("silverhand_hand_control", profile_name)

    rover_can_iface = _resolve_override(LaunchConfiguration("rover_can_iface").perform(context), rover_profile["can_iface"])
    rover_node_id = _resolve_override(LaunchConfiguration("rover_node_id").perform(context), rover_profile["node_id"])
    rover_queue_len = _resolve_override(LaunchConfiguration("rover_queue_len").perform(context), rover_profile["queue_len"])
    imu_name = _resolve_override(LaunchConfiguration("imu_name").perform(context), rover_profile["imu_name"])
    imu_frame_id = _resolve_override(LaunchConfiguration("imu_frame_id").perform(context), rover_profile["imu_frame_id"])
    imu_device_path = _resolve_override(
        LaunchConfiguration("imu_device_path").perform(context),
        rover_profile["imu_device_path"],
    )
    imu_vid = _resolve_override(LaunchConfiguration("imu_vid").perform(context), rover_profile["imu_vid"])
    imu_pid = _resolve_override(LaunchConfiguration("imu_pid").perform(context), rover_profile["imu_pid"])
    imu_report_size = _resolve_override(
        LaunchConfiguration("imu_report_size").perform(context),
        rover_profile["imu_report_size"],
    )
    use_imu_odometry = _resolve_override(
        LaunchConfiguration("use_imu_odometry").perform(context),
        rover_profile["use_imu_odometry"],
    ).lower()
    use_power_board = _resolve_override(
        LaunchConfiguration("use_power_board").perform(context),
        str(rover_profile["use_power_board"]).lower(),
    )
    power_board_client_node_id = _resolve_override(
        LaunchConfiguration("power_board_client_node_id").perform(context),
        rover_profile["power_board_client_node_id"],
    )

    description_file = PathJoinSubstitution(
        [FindPackageShare("silverhand_system_bringup"), "urdf", "silverhand_system.urdf.xacro"]
    )

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            description_file,
            " ",
            "use_mock_hardware:=",
            use_mock_hardware,
            " ",
            "rover_can_iface:=",
            rover_can_iface,
            " ",
            "rover_node_id:=",
            rover_node_id,
            " ",
            "rover_queue_len:=",
            rover_queue_len,
            " ",
            "imu_name:=",
            imu_name,
            " ",
            "imu_frame_id:=",
            imu_frame_id,
            " ",
            "imu_device_path:=",
            imu_device_path,
            " ",
            "imu_vid:=",
            imu_vid,
            " ",
            "imu_pid:=",
            imu_pid,
            " ",
            "imu_report_size:=",
            imu_report_size,
            " ",
            "arm_can_iface:=",
            str(arm_profile["can_iface"]),
            " ",
            "arm_node_id:=",
            str(arm_profile["node_id"]),
            " ",
            "arm_queue_len:=",
            str(arm_profile["queue_len"]),
            " ",
            "hand_can_iface:=",
            str(hand_profile["can_iface"]),
            " ",
            "hand_node_id:=",
            str(hand_profile["node_id"]),
            " ",
            "hand_queue_len:=",
            str(hand_profile["queue_len"]),
        ]
    )

    robot_description = {
        "robot_description": ParameterValue(robot_description_content, value_type=str)
    }
    robot_description_semantic = {
        "robot_description_semantic": load_file(
            "silverhand_system_bringup", "config/system.srdf"
        )
    }
    robot_description_kinematics = {
        "robot_description_kinematics": load_yaml(
            "silverhand_system_bringup", "config/kinematics.yaml"
        )
    }
    robot_description_planning = {
        "robot_description_planning": load_yaml(
            "silverhand_system_bringup", "config/joint_limits.yaml"
        )
    }
    moveit_controllers = load_yaml(
        "silverhand_system_bringup", "config/moveit_controllers.yaml"
    )
    ompl_config = load_yaml("silverhand_system_bringup", "config/ompl_planning.yaml")
    controllers_wheel = load_yaml("silverhand_system_bringup", "config/system_controllers_wheel.yaml")
    controllers_imu = load_yaml("silverhand_system_bringup", "config/system_controllers_imu.yaml")
    ekf_config_file = PathJoinSubstitution(
        [FindPackageShare("silverhand_rover_control"), "config", "ekf_imu.yaml"]
    )

    controllers_imu = copy.deepcopy(controllers_imu)
    controllers_imu["imu_sensor_broadcaster"]["ros__parameters"]["sensor_name"] = imu_name
    controllers_imu["imu_sensor_broadcaster"]["ros__parameters"]["frame_id"] = imu_frame_id

    planning_pipeline = {
        "planning_pipelines": ["ompl"],
        "default_planning_pipeline": "ompl",
        "ompl": ompl_config,
    }
    trajectory_execution = {
        "moveit_manage_controllers": False,
        "trajectory_execution.allowed_execution_duration_scaling": 1.2,
        "trajectory_execution.allowed_goal_duration_margin": 0.5,
        "trajectory_execution.allowed_start_tolerance": 0.01,
    }
    planning_scene_monitor_parameters = {
        "publish_planning_scene": True,
        "publish_geometry_updates": True,
        "publish_state_updates": True,
        "publish_transforms_updates": True,
        "publish_robot_description": True,
        "publish_robot_description_semantic": True,
    }

    if _is_truthy(use_mock_hardware):
        imu_enabled = False
        imu_reason = "mock hardware requested"
    elif use_imu_odometry == "true":
        imu_enabled = True
        imu_reason = "forced by use_imu_odometry:=true"
    elif use_imu_odometry == "false":
        imu_enabled = False
        imu_reason = "forced by use_imu_odometry:=false"
    else:
        imu_enabled = _detect_imu_available(imu_device_path, imu_vid, imu_pid)
        imu_reason = "IMU device detected" if imu_enabled else "IMU device not detected, using wheel odometry fallback"

    selected_controllers = controllers_imu if imu_enabled else controllers_wheel
    power_board_config = PathJoinSubstitution(
        [FindPackageShare("silverhand_rover_control"), "config", "power_board.yaml"]
    )
    with tempfile.NamedTemporaryFile(
        mode="w",
        prefix="silverhand_system_controllers_",
        suffix=".yaml",
        delete=False,
    ) as controllers_file:
        yaml.safe_dump(selected_controllers, controllers_file, sort_keys=False)
        selected_controllers_file = controllers_file.name

    power_board_use_mock = _is_truthy(use_mock_hardware)
    power_board_enabled = _is_truthy(use_power_board)
    power_board_node_id = int(power_board_client_node_id)
    rover_queue_len_value = int(rover_queue_len)

    actions = []

    if _is_truthy(run_system_bringup):
        actions.extend(
            [
                LogInfo(
                    msg=f"silverhand_system_bringup: {'IMU + EKF' if imu_enabled else 'wheel odometry'} mode selected ({imu_reason})"
                ),
                Node(
                    package="tf2_ros",
                    executable="static_transform_publisher",
                    output="screen",
                    arguments=["0", "0", "0", "0", "0", "0", "world", "odom"],
                ),
                Node(
                    package="robot_state_publisher",
                    executable="robot_state_publisher",
                    output="screen",
                    parameters=[robot_description],
                ),
                Node(
                    package="controller_manager",
                    executable="ros2_control_node",
                    output="screen",
                    parameters=[robot_description, selected_controllers_file],
                    remappings=[("/controller_manager/robot_description", "/robot_description")],
                ),
                Node(
                    package="controller_manager",
                    executable="spawner",
                    arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
                    output="screen",
                ),
                Node(
                    package="controller_manager",
                    executable="spawner",
                    arguments=["rover_base_controller", "--controller-manager", "/controller_manager"],
                    output="screen",
                ),
                Node(
                    package="controller_manager",
                    executable="spawner",
                    arguments=["arm_controller", "--controller-manager", "/controller_manager"],
                    output="screen",
                ),
                Node(
                    package="controller_manager",
                    executable="spawner",
                    arguments=["hand_controller", "--controller-manager", "/controller_manager"],
                    output="screen",
                ),
            ]
        )

        if power_board_enabled:
            actions.append(
                Node(
                    package="silverhand_rover_control",
                    executable="power_board_node",
                    output="screen",
                    parameters=[
                        power_board_config,
                        {
                            "use_mock": power_board_use_mock,
                            "can_iface": rover_can_iface,
                            "queue_len": rover_queue_len_value,
                            "node_id": power_board_node_id,
                        },
                    ],
                )
            )

        if imu_enabled:
            actions.extend(
                [
                    Node(
                        package="controller_manager",
                        executable="spawner",
                        arguments=["imu_sensor_broadcaster", "--controller-manager", "/controller_manager"],
                        output="screen",
                    ),
                    Node(
                        package="robot_localization",
                        executable="ekf_node",
                        name="ekf_filter_node",
                        output="screen",
                        parameters=[ekf_config_file],
                    ),
                ]
            )

    if _is_truthy(run_move_group):
        actions.append(
            Node(
                package="moveit_ros_move_group",
                executable="move_group",
                output="screen",
                parameters=[
                    robot_description,
                    robot_description_semantic,
                    robot_description_kinematics,
                    robot_description_planning,
                    planning_pipeline,
                    moveit_controllers,
                    trajectory_execution,
                    planning_scene_monitor_parameters,
                    {"use_sim_time": False},
                ],
            )
        )

    if _is_truthy(use_rviz):
        actions.append(
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                output="screen",
                arguments=["-d", rviz_config],
                parameters=[
                    robot_description,
                    robot_description_semantic,
                    robot_description_kinematics,
                    robot_description_planning,
                    planning_pipeline,
                    moveit_controllers,
                ],
            )
        )

    return actions


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("use_rviz", default_value="true"),
            DeclareLaunchArgument("run_system_bringup", default_value="true"),
            DeclareLaunchArgument("run_move_group", default_value="true"),
            DeclareLaunchArgument("use_mock_hardware", default_value="true"),
            DeclareLaunchArgument("rover_can_iface", default_value=""),
            DeclareLaunchArgument("rover_node_id", default_value=""),
            DeclareLaunchArgument("rover_queue_len", default_value=""),
            DeclareLaunchArgument("imu_name", default_value=""),
            DeclareLaunchArgument("imu_frame_id", default_value=""),
            DeclareLaunchArgument("imu_device_path", default_value=""),
            DeclareLaunchArgument("imu_vid", default_value=""),
            DeclareLaunchArgument("imu_pid", default_value=""),
            DeclareLaunchArgument("imu_report_size", default_value=""),
            DeclareLaunchArgument("use_imu_odometry", default_value=""),
            DeclareLaunchArgument("use_power_board", default_value=""),
            DeclareLaunchArgument("power_board_client_node_id", default_value=""),
            DeclareLaunchArgument(
                "rviz_config",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("silverhand_system_bringup"), "config", "moveit.rviz"]
                ),
            ),
            OpaqueFunction(function=create_runtime_nodes),
        ]
    )
