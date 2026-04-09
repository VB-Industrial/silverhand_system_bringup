from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_rviz = LaunchConfiguration("use_rviz")
    use_mock_hardware = LaunchConfiguration("use_mock_hardware")
    rviz_config = LaunchConfiguration("rviz_config")

    launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("silverhand_system_bringup"), "launch", "silverhand_system_common.launch.py"]
            )
        ),
        launch_arguments={
            "use_rviz": use_rviz,
            "run_arm_hand_bringup": "true",
            "run_move_group": "false",
            "use_mock_hardware": use_mock_hardware,
            "rviz_config": rviz_config,
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_rviz", default_value="false"),
            DeclareLaunchArgument("use_mock_hardware", default_value="true"),
            DeclareLaunchArgument(
                "rviz_config",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("silverhand_system_bringup"), "config", "view.rviz"]
                ),
            ),
            launch,
        ]
    )
