import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution


def generate_launch_description():
    ros_ws = LaunchConfiguration("ros_ws")
    host = LaunchConfiguration("host")
    port = LaunchConfiguration("port")

    teleop_script = PathJoinSubstitution(
        [ros_ws, "src", "silverhand_rover_teleop", "silverhand_rover_teleop_start.sh"]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "ros_ws",
                default_value=EnvironmentVariable("ROS_WS", default_value=os.path.expanduser("~/silver_ws")),
            ),
            DeclareLaunchArgument("host", default_value="0.0.0.0"),
            DeclareLaunchArgument("port", default_value="4174"),
            ExecuteProcess(
                cmd=[teleop_script],
                additional_env={"HOST": host, "PORT": port},
                output="screen",
            ),
        ]
    )
