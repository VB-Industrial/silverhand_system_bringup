from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_mock_hardware = LaunchConfiguration("use_mock_hardware")
    can_iface = LaunchConfiguration("can_iface")
    node_id = LaunchConfiguration("node_id")
    queue_len = LaunchConfiguration("queue_len")

    launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("silverhand_rover_control"), "launch", "silverhand_rover_bringup.launch.py"]
            )
        ),
        launch_arguments={
            "use_mock_hardware": use_mock_hardware,
            "can_iface": can_iface,
            "node_id": node_id,
            "queue_len": queue_len,
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_mock_hardware", default_value="true"),
            DeclareLaunchArgument("can_iface", default_value="vcan1"),
            DeclareLaunchArgument("node_id", default_value="110"),
            DeclareLaunchArgument("queue_len", default_value="1000"),
            launch,
        ]
    )
