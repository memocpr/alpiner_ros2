#!/usr/bin/env python3

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    ros2_app_dir = get_package_share_directory('ros2_application')

    default_waypoints_file = os.path.join(
        ros2_app_dir,
        'config',
        'gps_waypoints.yaml'
    )

    waypoints_file = LaunchConfiguration('waypoints_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    gps_waypoint_follower_node = Node(
        package='ros2_application',
        executable='gps_waypoint_follower',
        name='gps_waypoint_follower',
        output='screen',
        arguments=[waypoints_file],
        parameters=[{'use_sim_time': use_sim_time}],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true'
        ),
        DeclareLaunchArgument(
            'waypoints_file',
            default_value=default_waypoints_file
        ),
        gps_waypoint_follower_node,
    ])