import os
import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
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


def generate_launch_description():
    use_rviz = LaunchConfiguration("use_rviz")
    run_robot_bringup = LaunchConfiguration("run_robot_bringup")
    run_move_group = LaunchConfiguration("run_move_group")
    use_mock_hardware = LaunchConfiguration("use_mock_hardware")
    arm_can_iface = LaunchConfiguration("arm_can_iface")
    arm_node_id = LaunchConfiguration("arm_node_id")
    hand_can_iface = LaunchConfiguration("hand_can_iface")
    hand_node_id = LaunchConfiguration("hand_node_id")
    rviz_config = LaunchConfiguration("rviz_config")

    description_file = PathJoinSubstitution(
        [FindPackageShare("silverhand_system_bringup"), "urdf", "silverhand_arm_hand.urdf.xacro"]
    )
    ros2_controllers_file = PathJoinSubstitution(
        [FindPackageShare("silverhand_system_bringup"), "config", "ros2_controllers.yaml"]
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
            "arm_can_iface:=",
            arm_can_iface,
            " ",
            "arm_node_id:=",
            arm_node_id,
            " ",
            "hand_can_iface:=",
            hand_can_iface,
            " ",
            "hand_node_id:=",
            hand_node_id,
        ]
    )

    robot_description = {"robot_description": robot_description_content}
    robot_description_semantic = {
        "robot_description_semantic": load_file(
            "silverhand_system_bringup", "config/silverhand.srdf"
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

    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        output="screen",
        arguments=["0", "0", "0", "0", "0", "0", "world", "base_link"],
        condition=IfCondition(run_robot_bringup),
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
        condition=IfCondition(run_robot_bringup),
    )

    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        output="screen",
        parameters=[robot_description, ros2_controllers_file],
        remappings=[("/controller_manager/robot_description", "/robot_description")],
        condition=IfCondition(run_robot_bringup),
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
        output="screen",
        condition=IfCondition(run_robot_bringup),
    )

    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller", "--controller-manager", "/controller_manager"],
        output="screen",
        condition=IfCondition(run_robot_bringup),
    )

    hand_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["hand_controller", "--controller-manager", "/controller_manager"],
        output="screen",
        condition=IfCondition(run_robot_bringup),
    )

    move_group = Node(
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
        condition=IfCondition(run_move_group),
    )

    rviz = Node(
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
        condition=IfCondition(use_rviz),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_rviz", default_value="true"),
            DeclareLaunchArgument("run_robot_bringup", default_value="true"),
            DeclareLaunchArgument("run_move_group", default_value="true"),
            DeclareLaunchArgument("use_mock_hardware", default_value="true"),
            DeclareLaunchArgument("arm_can_iface", default_value="can0"),
            DeclareLaunchArgument("arm_node_id", default_value="100"),
            DeclareLaunchArgument("hand_can_iface", default_value="can0"),
            DeclareLaunchArgument("hand_node_id", default_value="120"),
            DeclareLaunchArgument(
                "rviz_config",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("silverhand_system_bringup"), "config", "moveit.rviz"]
                ),
            ),
            static_tf,
            robot_state_publisher,
            ros2_control_node,
            joint_state_broadcaster_spawner,
            arm_controller_spawner,
            hand_controller_spawner,
            move_group,
            rviz,
        ]
    )
