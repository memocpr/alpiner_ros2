"""Launch file for local mock GNSS + UKF localization pipeline."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for GNSS mock localization pipeline."""

    ros2_app_dir = get_package_share_directory('ros2_application')
    ukf_params_file = os.path.join(ros2_app_dir, 'config', 'ukf_params.yaml')

    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation clock if available',
    )

    sim_odometry_node = Node(
        package='ros2_application',
        executable='sim_odometry_publisher',
        name='sim_odometry',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
    )

    sim_imu_node = Node(
        package='ros2_application',
        executable='sim_imu_publisher',
        name='sim_imu',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
    )

    sim_gnss_node = Node(
        package='ros2_application',
        executable='sim_gnss_publisher',
        name='sim_gnss',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'frame_id': 'gnss_link',
        }],
    )

    ukf_node = Node(
        package='robot_localization',
        executable='ukf_node',
        name='ukf_filter_node',
        output='screen',
        parameters=[ukf_params_file, {
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
    )

    navsat_transform_node = Node(
        package='robot_localization',
        executable='navsat_transform_node',
        name='navsat_transform_node',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'frequency': 30.0,
            'delay': 0.0,
            'magnetic_declination_radians': 0.0,
            'yaw_offset': 0.0,
            'zero_altitude': True,
            'broadcast_utm_transform': False,
            'publish_filtered_gps': True,
            'use_odometry_yaw': True,
            'wait_for_datum': False,
        }],
        remappings=[
            ('imu/data', '/imu/data'),
            ('gps/fix', '/gps/fix'),
            ('gps/filtered', '/gps/filtered'),
            ('odometry/filtered', '/odometry/filtered'),
        ],
    )

    return LaunchDescription([
        use_sim_time,
        sim_odometry_node,
        sim_imu_node,
        sim_gnss_node,
        ukf_node,
        navsat_transform_node,
    ])