"""Launch file for RTAB-Map mapping stage."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for mapping pipeline."""

    ros2_app_dir = get_package_share_directory('ros2_application')
    rtabmap_params_file = os.path.join(ros2_app_dir, 'config', 'rtabmap_params.yaml')

    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation clock if available',
    )

    use_sim_scan = DeclareLaunchArgument(
        'use_sim_scan',
        default_value='true',
        description='Use simulated LaserScan input',
    )

    odom_topic = DeclareLaunchArgument(
        'odom_topic',
        default_value='/odometry/filtered',
        description='Odometry topic used by RTAB-Map',
    )

    scan_topic = DeclareLaunchArgument(
        'scan_topic',
        default_value='/scan',
        description='LaserScan topic used by RTAB-Map',
    )

    sim_scan_node = Node(
        package='ros2_application',
        executable='sim_scan_publisher',
        name='sim_scan',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
        condition=IfCondition(LaunchConfiguration('use_sim_scan')),
    )

    sim_scan_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='sim_scan_static_tf',
        arguments=['0.0', '0.0', '1.0', '0.0', '0.0', '0.0', 'base_link', 'laser_frame'],
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
        condition=IfCondition(LaunchConfiguration('use_sim_scan')),
    )

    rtabmap_node = Node(
        package='rtabmap_slam',
        executable='rtabmap',
        name='rtabmap',
        output='screen',
        parameters=[rtabmap_params_file, {
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
        remappings=[
            ('odom', LaunchConfiguration('odom_topic')),
            ('scan', LaunchConfiguration('scan_topic')),
        ],
    )

    return LaunchDescription([
        use_sim_time,
        use_sim_scan,
        odom_topic,
        scan_topic,
        sim_scan_node,
        sim_scan_tf,
        rtabmap_node,
    ])

