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
                    "DEPRECATED: silverhand_system_rover_real.launch.py is a legacy alias. "
                    "Use silverhand_system_rover_ros_control.launch.py."
                )
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [FindPackageShare("silverhand_system_bringup"), "launch", "silverhand_system_rover_ros_control.launch.py"]
                    )
                ),
            ),
        ]
    )
