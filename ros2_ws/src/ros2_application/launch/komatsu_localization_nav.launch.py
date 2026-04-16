#!/usr/bin/env python3

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    ros2_app_dir = get_package_share_directory('ros2_application')

    ukf_local_params = os.path.join(ros2_app_dir, 'config', 'ukf_params.yaml')
    ukf_global_params = os.path.join(ros2_app_dir, 'config', 'ukf_global.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_global_localization = LaunchConfiguration('use_global_localization')

    return LaunchDescription([

        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('use_global_localization', default_value='true'),

        # Local EKF: wheel odom (/odom) + IMU -> odom frame -> /odometry/filtered_local
        Node(
            package='robot_localization',
            executable='ukf_node',
            name='ukf_filter_node',
            output='screen',
            parameters=[
                ukf_local_params,
                {
                    'use_sim_time': use_sim_time,
                    'publish_tf': True,
                    'world_frame': 'odom',
                    'odom_frame': 'odom',
                    'map_frame': 'map',
                    'base_link_frame': 'base_footprint',
                    'odom0': '/odom',
                    'imu0': '/imu/data',
                }
            ],
            remappings=[('odometry/filtered', '/odometry/filtered_local')],
        ),

        # navsat_transform: /gps/fix + /imu/data + /odometry/filtered_local -> /odometry/gps
        Node(
            package='robot_localization',
            executable='navsat_transform_node',
            name='navsat_transform_node',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'frequency': 30.0,
                'delay': 3.0,
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
            condition=IfCondition(use_global_localization),
        ),

        # Global EKF: /odometry/gps + /odometry/filtered_local -> map frame -> TF map->odom
        Node(
            package='robot_localization',
            executable='ukf_node',
            name='ukf_global_node',
            output='screen',
            parameters=[
                ukf_global_params,
                {
                    'use_sim_time': use_sim_time,
                    'publish_tf': True,
                    'world_frame': 'map',
                    'map_frame': 'map',
                    'odom_frame': 'odom',
                    'base_link_frame': 'base_footprint',
                    'odom0': '/odometry/gps',
                    'odom1': '/odometry/filtered_local',
                }
            ],
            condition=IfCondition(use_global_localization),
        ),

        # GNSS antenna TF: matches offset defined in URDF gnss_joint
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='gnss_static_tf',
            arguments=['-1.0', '0.0', '2.0', '0', '0', '0', 'base_link', 'gnss_link'],
            parameters=[{'use_sim_time': use_sim_time}],
        ),
    ])