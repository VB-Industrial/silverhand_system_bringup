from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription(
        [
            LogInfo(
                msg=(
                    "DEPRECATED: silverhand_system_real_rviz.launch.py is a legacy alias. "
                    "Use silverhand_system_moveit.launch.py use_mock_hardware:=false."
                )
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [FindPackageShare("silverhand_system_bringup"), "launch", "silverhand_system_moveit.launch.py"]
                    )
                ),
                launch_arguments={
                    "use_rviz": "true",
                    "use_mock_hardware": "false",
                }.items(),
            ),
        ]
    )
