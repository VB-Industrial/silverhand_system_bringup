from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_rviz = LaunchConfiguration("use_rviz")
    rviz_config = LaunchConfiguration("rviz_config")

    return LaunchDescription(
        [
            LogInfo(
                msg=(
                    "DEPRECATED: silverhand_system_arm_hand_real.launch.py is a legacy alias. "
                    "Use silverhand_system_arm_hand_ros_control.launch.py."
                )
            ),
            DeclareLaunchArgument("use_rviz", default_value="false"),
            DeclareLaunchArgument(
                "rviz_config",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("silverhand_system_bringup"), "config", "view.rviz"]
                ),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [FindPackageShare("silverhand_system_bringup"), "launch", "silverhand_system_arm_hand_ros_control.launch.py"]
                    )
                ),
                launch_arguments={
                    "use_rviz": use_rviz,
                    "rviz_config": rviz_config,
                }.items(),
            ),
        ]
    )
