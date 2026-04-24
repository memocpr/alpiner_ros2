#!/usr/bin/env python3
import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory
def generate_launch_description():
    # Get package directories
    robot_description_dir = get_package_share_directory('robot_description')
    # Path to URDF xacro file
    urdf_file = os.path.join(robot_description_dir, 'urdf/komatsu', 'komatsu.urdf.xacro')
    # Path to RViz config
    rviz_config_file = os.path.join(robot_description_dir, 'rviz', 'urdf_config.rviz')
    # Process xacro file
    robot_description_content = ParameterValue(
        Command(['xacro', ' ', urdf_file]),
        value_type=str
    )
    # Robot State Publisher node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': False
        }]
    )
    # Joint State Publisher GUI node
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen'
    )
    # RViz node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file]
    )
    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])
