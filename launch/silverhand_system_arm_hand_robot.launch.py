from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_mock_hardware = LaunchConfiguration("use_mock_hardware")

    launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("silverhand_system_bringup"), "launch", "silverhand_system_common.launch.py"]
            )
        ),
        launch_arguments={
            "use_rviz": "false",
            "run_arm_hand_bringup": "true",
            "run_move_group": "true",
            "use_mock_hardware": use_mock_hardware,
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_mock_hardware", default_value="true"),
            launch,
        ]
    )
