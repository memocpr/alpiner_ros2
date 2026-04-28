#!/usr/bin/env python3

import os
import re

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def _launch_setup(context):
    xacro_file_path = LaunchConfiguration('xacro_file').perform(context)
    robot_description_xml = xacro.process_file(xacro_file_path).toxml()
    # gazebo_ros2_control passes robot_description through CLI args where XML comments can break parsing.
    robot_description_xml = re.sub(r'<!--.*?-->', '', robot_description_xml, flags=re.DOTALL)

    return [
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'robot_description': robot_description_xml,
            }],
        ),
    ]


def generate_launch_description():
    default_xacro_file = os.path.join(
        get_package_share_directory('robot_description'),
        'urdf',
        'komatsu',
        'komatsu_gazebo.urdf.xacro'
    )
    xacro_file = LaunchConfiguration('xacro_file')

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
        OpaqueFunction(function=_launch_setup),
    ])
