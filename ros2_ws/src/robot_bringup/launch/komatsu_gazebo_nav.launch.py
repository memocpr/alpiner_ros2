#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, LogInfo
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():

    bringup_dir = get_package_share_directory('robot_bringup')
    robot_desc_dir = get_package_share_directory('robot_description')
    ros2_app_dir = get_package_share_directory('ros2_application')
    gazebo_dir = get_package_share_directory('gazebo_ros')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_global_localization = LaunchConfiguration('use_global_localization')
    autostart = LaunchConfiguration('autostart')
    map_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    enable_mapviz = LaunchConfiguration('enable_mapviz')

    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')
    z_pose = LaunchConfiguration('z_pose')
    map_to_odom_x = LaunchConfiguration('map_to_odom_x')
    map_to_odom_y = LaunchConfiguration('map_to_odom_y')

    world = os.path.join(
        bringup_dir,
        'worlds',
        'simple_world',
        'field.sdf'
    )

    default_map_file = os.path.join(
        bringup_dir,
        'maps',
        'field_map.yaml'
    )

    default_params_file = os.path.join(
        bringup_dir,
        'config',
        'komatsu_nav2_params.yaml'
    )

    default_rviz_config = os.path.join(
        nav2_bringup_dir,
        'rviz',
        'nav2_default_view.rviz'
    )

    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_dir, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world}.items()
    )

    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_dir, 'launch', 'gzclient.launch.py')
        )
    )

    robot_state_publisher_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(robot_desc_dir, 'launch', 'robot_state_publisher.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time
        }.items()
    )

    spawn_robot_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(robot_desc_dir, 'launch', 'spawn_my_robot.launch.py')
        ),
        launch_arguments={
            'x_pose': x_pose,
            'y_pose': y_pose,
            'z_pose': z_pose,
        }.items()
    )

    localization_launch_file = os.path.join(
        ros2_app_dir,
        'launch',
        'komatsu_localization_nav.launch.py'
    )

    localization_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            localization_launch_file
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'use_global_localization': use_global_localization,
        }.items()
    )

    localization_include_log = LogInfo(
        msg=[
            'Including localization launch: ',
            localization_launch_file,
            ' with use_global_localization:=',
            use_global_localization,
        ]
    )

    gnss_enabled_log = LogInfo(
        condition=IfCondition(use_global_localization),
        msg='GNSS global localization mode ENABLED: GNSS localization ON, map_server OFF, static map->odom TF OFF.',
    )

    gnss_disabled_log = LogInfo(
        condition=UnlessCondition(use_global_localization),
        msg='Fallback localization mode ENABLED: GNSS localization OFF, map_server ON, static map->odom TF ON.',
    )

    map_to_odom_static_tf_cmd = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='map_to_odom_static_tf',
        arguments=[map_to_odom_x, map_to_odom_y, '0', '0', '0', '0', 'map', 'odom'],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=UnlessCondition(use_global_localization),
    )

    map_server_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros2_app_dir, 'launch', 'komatsu_map_server_nav.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'map': map_file,
        }.items(),
        condition=UnlessCondition(use_global_localization),
    )

    mapviz_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros2_app_dir, 'launch', 'komatsu_mapviz_nav.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
        }.items(),
        condition=IfCondition(enable_mapviz),
    )

    nav2_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_dir, 'launch', 'komatsu_nav2_nav.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': params_file,
            'autostart': autostart,
        }.items()
    )

    rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', default_rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true'
        ),
        DeclareLaunchArgument(
            'autostart',
            default_value='true'
        ),
        DeclareLaunchArgument(
            'use_global_localization',
            default_value='true',
            description='true: GNSS mode, false: static map fallback mode'
        ),
        DeclareLaunchArgument(
            'enable_mapviz',
            default_value='true',
            description='Launch Mapviz support alongside bringup'
        ),
        DeclareLaunchArgument(
            'map',
            default_value=default_map_file
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params_file
        ),
        DeclareLaunchArgument(
            'x_pose',
            default_value='-24.1'
        ),
        DeclareLaunchArgument(
            'y_pose',
            default_value='-11.3'
        ),
        DeclareLaunchArgument(
            'z_pose',
            default_value='0.0'
        ),
        DeclareLaunchArgument(
            'map_to_odom_x',
            default_value=PythonExpression(['-(', x_pose, ') + 61.6'])
        ),
        DeclareLaunchArgument(
            'map_to_odom_y',
            default_value=PythonExpression(['-(', y_pose, ') + 23.7'])
        ),
        gzserver_cmd,
        gzclient_cmd,
        robot_state_publisher_cmd,
        spawn_robot_cmd,
        localization_include_log,
        gnss_enabled_log,
        gnss_disabled_log,
        localization_cmd,
        map_to_odom_static_tf_cmd,
        map_server_cmd,
        mapviz_cmd,
        nav2_cmd,
        rviz_cmd,
    ])