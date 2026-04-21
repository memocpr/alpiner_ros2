#!/usr/bin/env python3

import os
import tempfile

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _prepare_mapviz_config(config_path: str) -> str:
    with open(config_path, 'r', encoding='utf-8') as config_file:
        config_contents = config_file.read()

    expanded_contents = os.path.expandvars(config_contents)

    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.mvc', prefix='komatsu_mapviz_', delete=False, encoding='utf-8'
    ) as temp_config:
        temp_config.write(expanded_contents)
        return temp_config.name


def generate_launch_description():

    ros2_app_dir = get_package_share_directory('ros2_application')

    use_sim_time = LaunchConfiguration('use_sim_time')

    mapviz_config = _prepare_mapviz_config(os.path.join(
        ros2_app_dir,
        'config',
        'gps_wpf_demo.mvc'
    ))

    return LaunchDescription([

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true'
        ),

        Node(
            package='mapviz',
            executable='mapviz',
            name='mapviz',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'config': mapviz_config
            }]
        ),

        Node(
            package='ros2_application',
            executable='send_nav_goal',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}]
        ),

        Node(
            package='swri_transform_util',
            executable='initialize_origin.py',
            name='initialize_origin',
            output='screen',
            remappings=[
                ('fix', 'gps/fix'),
            ],
            parameters=[
                {'use_sim_time': use_sim_time},
                {'local_xy_frame': 'map'},
                {'local_xy_origin': 'auto'}
            ],
        ),

#        Node(
#            package='tf2_ros',
#            executable='static_transform_publisher',
#            name='mapviz_tf',
#            arguments=['--frame-id', 'map', '--child-frame-id', 'origin'],
#            parameters=[{'use_sim_time': use_sim_time}]
#        ),

    ])