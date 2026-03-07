"""Launch file for RTAB-Map mapping stage with real hardware sensors."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for mapping pipeline with hardware sensors."""

    ros2_app_dir = get_package_share_directory('ros2_application')
    rtabmap_params_file = os.path.join(ros2_app_dir, 'config', 'rtabmap_params.yaml')

    odom_topic = DeclareLaunchArgument(
        'odom_topic',
        default_value='/odometry/filtered',
        description='Odometry topic used by RTAB-Map',
    )

    scan_topic = DeclareLaunchArgument(
        'scan_topic',
        default_value='/scan',
        description='LaserScan topic from real hardware',
    )

    laser_frame = DeclareLaunchArgument(
        'laser_frame',
        default_value='laser_frame',
        description='Frame ID for real laser/LiDAR sensor',
    )

    rtabmap_node = Node(
        package='rtabmap_slam',
        executable='rtabmap',
        name='rtabmap',
        output='screen',
        parameters=[rtabmap_params_file],
        remappings=[
            ('odom', LaunchConfiguration('odom_topic')),
            ('scan', LaunchConfiguration('scan_topic')),
        ],
    )

    return LaunchDescription([
        odom_topic,
        scan_topic,
        laser_frame,
        rtabmap_node,
    ])

