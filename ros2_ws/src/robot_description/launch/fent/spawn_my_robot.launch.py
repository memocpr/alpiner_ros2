#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')
    z_pose = LaunchConfiguration('z_pose')
    entity_name = LaunchConfiguration('entity_name')
    robot_description_topic = LaunchConfiguration('robot_description_topic')

    return LaunchDescription([
        DeclareLaunchArgument('x_pose', default_value='0.0', description='Spawn x position'),
        DeclareLaunchArgument('y_pose', default_value='0.0', description='Spawn y position'),
        DeclareLaunchArgument('z_pose', default_value='0.0', description='Spawn z position'),
        DeclareLaunchArgument('entity_name', default_value='fent', description='Gazebo entity name'),
        DeclareLaunchArgument(
            'robot_description_topic',
            default_value='robot_description',
            description='Topic containing URDF XML'
        ),
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            output='screen',
            arguments=[
                '-entity', entity_name,
                '-topic', robot_description_topic,
                '-x', x_pose,
                '-y', y_pose,
                '-z', z_pose,
            ],
        ),
    ])

