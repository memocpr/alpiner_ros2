"""Launch file for GNSS localization pipeline (local UKF + navsat_transform + global UKF)."""
import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    """Generate launch description for localization pipeline."""

    ros2_app_dir = get_package_share_directory('ros2_application')
    ukf_params_file = os.path.join(ros2_app_dir, 'config', 'ukf_params.yaml')
    ukf_global_params_file = os.path.join(ros2_app_dir, 'config', 'ukf_global.yaml')

    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation clock if available',
    )

    use_sim_odometry = DeclareLaunchArgument(
        'use_sim_odometry',
        default_value='true',
        description='Use simulated odometry input',
    )

    use_sim_imu = DeclareLaunchArgument(
        'use_sim_imu',
        default_value='true',
        description='Use simulated IMU input',
    )

    use_mock_gnss = DeclareLaunchArgument(
        'use_mock_gnss',
        default_value='true',
        description='Use simulated GNSS input instead of real /gps/fix',
    )

    ukf_local_node_sim = Node(
        package='robot_localization',
        executable='ukf_node',
        name='ukf_local_node',
        output='screen',
        parameters=[ukf_params_file, {
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
        remappings=[
            ('odometry/filtered', '/odometry/filtered_local'),
        ],
        condition=IfCondition(LaunchConfiguration('use_sim_odometry')),
    )

    ukf_local_node_gazebo = Node(
        package='robot_localization',
        executable='ukf_node',
        name='ukf_local_node',
        output='screen',
        parameters=[ukf_params_file, {
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'odom0': '/odom',
        }],
        remappings=[
            ('odometry/filtered', '/odometry/filtered_local'),
        ],
        condition=UnlessCondition(LaunchConfiguration('use_sim_odometry')),
    )

    ukf_global_node = Node(
        package='robot_localization',
        executable='ukf_node',
        name='ukf_global_node',
        output='screen',
        parameters=[ukf_global_params_file, {
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
    )

    sim_odometry_node = Node(
        package='ros2_application',
        executable='sim_odometry_publisher',
        name='sim_odometry',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
        condition=IfCondition(LaunchConfiguration('use_sim_odometry')),
    )

    sim_imu_node = Node(
        package='ros2_application',
        executable='sim_imu_publisher',
        name='sim_imu',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
        condition=IfCondition(LaunchConfiguration('use_sim_imu')),
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
        condition=IfCondition(LaunchConfiguration('use_mock_gnss')),
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
            ('odometry/filtered', '/odometry/filtered_local'),
        ],
    )

    return LaunchDescription([
        use_sim_time,
        use_sim_odometry,
        use_sim_imu,
        use_mock_gnss,
        ukf_local_node_sim,
        ukf_local_node_gazebo,
        ukf_global_node,
        sim_odometry_node,
        sim_imu_node,
        sim_gnss_node,
        navsat_transform_node,
    ])