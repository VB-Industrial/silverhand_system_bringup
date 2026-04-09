import os
import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
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


def create_runtime_nodes(context):
    use_rviz = LaunchConfiguration("use_rviz").perform(context)
    run_arm_bringup = LaunchConfiguration("run_arm_bringup").perform(context)
    run_move_group = LaunchConfiguration("run_move_group").perform(context)
    use_mock_hardware = LaunchConfiguration("use_mock_hardware").perform(context)
    rviz_config = LaunchConfiguration("rviz_config").perform(context)

    profile_name = "mock" if _is_truthy(use_mock_hardware) else "ros_control"
    arm_profile = load_profile("silverhand_arm_control", profile_name)

    description_file = PathJoinSubstitution(
        [FindPackageShare("silverhand_arm_control"), "urdf", "silverhand.urdf.xacro"]
    )
    controllers_file = PathJoinSubstitution(
        [FindPackageShare("silverhand_arm_control"), "config", "controllers.yaml"]
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
            "can_iface:=",
            str(arm_profile["can_iface"]),
            " ",
            "node_id:=",
            str(arm_profile["node_id"]),
            " ",
            "queue_len:=",
            str(arm_profile["queue_len"]),
        ]
    )

    robot_description = {"robot_description": robot_description_content}
    robot_description_semantic = {
        "robot_description_semantic": load_file(
            "silverhand_system_bringup", "config/arm.srdf"
        )
    }
    robot_description_kinematics = {
        "robot_description_kinematics": load_yaml(
            "silverhand_system_bringup", "config/arm_kinematics.yaml"
        )
    }
    robot_description_planning = {
        "robot_description_planning": load_yaml(
            "silverhand_system_bringup", "config/arm_joint_limits.yaml"
        )
    }
    moveit_controllers = load_yaml(
        "silverhand_system_bringup", "config/arm_moveit_controllers.yaml"
    )
    ompl_config = load_yaml("silverhand_system_bringup", "config/ompl_planning.yaml")

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

    actions = []

    if _is_truthy(run_arm_bringup):
        actions.extend(
            [
                Node(
                    package="tf2_ros",
                    executable="static_transform_publisher",
                    output="screen",
                    arguments=["0", "0", "0", "0", "0", "0", "world", "base_link"],
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
                    parameters=[robot_description, controllers_file],
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
                    arguments=["arm_controller", "--controller-manager", "/controller_manager"],
                    output="screen",
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
            DeclareLaunchArgument("run_arm_bringup", default_value="true"),
            DeclareLaunchArgument("run_move_group", default_value="true"),
            DeclareLaunchArgument("use_mock_hardware", default_value="true"),
            DeclareLaunchArgument(
                "rviz_config",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("silverhand_system_bringup"), "config", "moveit.rviz"]
                ),
            ),
            OpaqueFunction(function=create_runtime_nodes),
        ]
    )
