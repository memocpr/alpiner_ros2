#!/usr/bin/env python3

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, RegisterEventHandler
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnProcessExit, OnProcessStart
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    ros2_app_dir = get_package_share_directory('ros2_application')

    ukf_local_params = os.path.join(ros2_app_dir, 'config', 'ukf_params.yaml')
    ukf_global_params = os.path.join(ros2_app_dir, 'config', 'ukf_global.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_global_localization = LaunchConfiguration('use_global_localization')
    odom_topic = LaunchConfiguration('odom_topic')
    yaw_offset = LaunchConfiguration('yaw_offset')
    wait_for_datum = LaunchConfiguration('wait_for_datum')

    # Local UKF: publishes odom -> base_footprint
    ukf_local_node = Node(
        package='robot_localization',
        executable='ukf_node',
        name='ukf_filter_node_odom',
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
                'odom0': odom_topic,
                'imu0': '/imu/data',
            }
        ],
        remappings=[
            ('odometry/filtered', '/odometry/filtered_local'),
        ],
    )

    gps_covariance_relay_node = Node(
        package='ros2_application',
        executable='gps_covariance_relay',
        name='gps_covariance_relay',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(use_global_localization),
    )

    navsat_transform_node = Node(
        package='robot_localization',
        executable='navsat_transform_node',
        name='navsat_transform_node',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'frequency': 30.0,
            'delay': 3.0,
            'magnetic_declination_radians': 0.0,
            'yaw_offset': yaw_offset,
            'zero_altitude': True,
            'broadcast_utm_transform': False,
            'publish_filtered_gps': True,
            'use_odometry_yaw': True,
            'wait_for_datum': wait_for_datum,
        }],
        remappings=[
            ('imu/data', '/imu/data'),
            ('gps/fix', '/gps/fix_cov'),
            ('gps/filtered', '/gps/filtered'),
            ('odometry/gps', '/odometry/gps'),
            ('odometry/filtered', '/odometry/filtered'),
        ],
        condition=IfCondition(use_global_localization),
    )

    # Global UKF: publishes dynamic map -> odom from GNSS
    ukf_global_node = Node(
        package='robot_localization',
        executable='ukf_node',
        name='ukf_filter_node_map',
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
                'odom0': odom_topic,
                'odom1': '/odometry/gps',
                'imu0': '/imu/data',
            }
        ],
        remappings=[
            ('odometry/filtered', '/odometry/filtered'),
        ],
        condition=IfCondition(use_global_localization),
    )

    gnss_enabled_log = LogInfo(
        condition=IfCondition(use_global_localization),
        msg=(
            'GNSS global localization ENABLED. '
            'Starting gps_covariance_relay, navsat_transform_node, '
            'ukf_filter_node_odom, and ukf_filter_node_map.'
        ),
    )

    gnss_disabled_log = LogInfo(
        condition=UnlessCondition(use_global_localization),
        msg=(
            'GNSS global localization DISABLED. '
            'Only ukf_filter_node_odom will run.'
        ),
    )

    gps_covariance_relay_start_log = RegisterEventHandler(
        OnProcessStart(
            target_action=gps_covariance_relay_node,
            on_start=[LogInfo(msg='Started gps_covariance_relay: /gps/fix -> /gps/fix_cov')],
        ),
        condition=IfCondition(use_global_localization),
    )

    navsat_transform_start_log = RegisterEventHandler(
        OnProcessStart(
            target_action=navsat_transform_node,
            on_start=[LogInfo(msg='Started navsat_transform_node: consumes /gps/fix_cov and publishes /odometry/gps')],
        ),
        condition=IfCondition(use_global_localization),
    )

    ukf_global_start_log = RegisterEventHandler(
        OnProcessStart(
            target_action=ukf_global_node,
            on_start=[LogInfo(msg='Started ukf_filter_node_map: dynamic map->odom enabled')],
        ),
        condition=IfCondition(use_global_localization),
    )

    gps_covariance_relay_exit_log = RegisterEventHandler(
        OnProcessExit(
            target_action=gps_covariance_relay_node,
            on_exit=[LogInfo(msg='WARNING: gps_covariance_relay exited.')],
        ),
        condition=IfCondition(use_global_localization),
    )

    navsat_transform_exit_log = RegisterEventHandler(
        OnProcessExit(
            target_action=navsat_transform_node,
            on_exit=[LogInfo(msg='WARNING: navsat_transform_node exited. /odometry/gps will stop updating.')],
        ),
        condition=IfCondition(use_global_localization),
    )

    ukf_global_exit_log = RegisterEventHandler(
        OnProcessExit(
            target_action=ukf_global_node,
            on_exit=[LogInfo(msg='WARNING: ukf_filter_node_map exited. Dynamic map->odom is no longer being published.')],
        ),
        condition=IfCondition(use_global_localization),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true'
        ),
        DeclareLaunchArgument(
            'odom_topic',
            default_value='/odom',
            description='Odometry source topic for local/global UKF (Gazebo default: /odom)',
        ),
        DeclareLaunchArgument(
            'use_global_localization',
            default_value='true',
            description='Enable GNSS relay + navsat_transform + global UKF',
        ),
        DeclareLaunchArgument(
            'yaw_offset',
            default_value='0.0',
            description='ENU heading offset for navsat_transform_node',
        ),
        DeclareLaunchArgument(
            'wait_for_datum',
            default_value='false',
            description='Wait for manual datum initialization before navsat_transform starts publishing',
        ),

        gnss_enabled_log,
        gnss_disabled_log,

        ukf_local_node,
        gps_covariance_relay_node,
        navsat_transform_node,
        ukf_global_node,

        gps_covariance_relay_start_log,
        navsat_transform_start_log,
        ukf_global_start_log,

        gps_covariance_relay_exit_log,
        navsat_transform_exit_log,
        ukf_global_exit_log,
    ])