from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    arm_can_iface = LaunchConfiguration("arm_can_iface")
    arm_node_id = LaunchConfiguration("arm_node_id")
    hand_can_iface = LaunchConfiguration("hand_can_iface")
    hand_node_id = LaunchConfiguration("hand_node_id")

    launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("silverhand_system_bringup"), "launch", "silverhand_system_common.launch.py"]
            )
        ),
        launch_arguments={
            "use_rviz": "true",
            "run_robot_bringup": "true",
            "run_move_group": "true",
            "use_mock_hardware": "false",
            "arm_can_iface": arm_can_iface,
            "arm_node_id": arm_node_id,
            "hand_can_iface": hand_can_iface,
            "hand_node_id": hand_node_id,
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("arm_can_iface", default_value="can0"),
            DeclareLaunchArgument("arm_node_id", default_value="100"),
            DeclareLaunchArgument("hand_can_iface", default_value="can0"),
            DeclareLaunchArgument("hand_node_id", default_value="120"),
            launch,
        ]
    )
