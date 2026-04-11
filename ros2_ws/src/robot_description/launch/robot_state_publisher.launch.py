#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    default_xacro_file = os.path.join(
        get_package_share_directory('robot_description'),
        'urdf',
        'komatsu_gazebo.urdf.xacro'
    )
    xacro_file = LaunchConfiguration('xacro_file')

    robot_description = ParameterValue(
        Command(['xacro', ' ', xacro_file]),
        value_type=str
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock'
        ),
        DeclareLaunchArgument(
            'xacro_file',
            default_value=default_xacro_file,
            description='Absolute path to robot xacro file'
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'robot_description': robot_description,
            }],
        ),
    ])
