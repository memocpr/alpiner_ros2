#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    my_robot_launch_dir = os.path.join(get_package_share_directory('robot_description'), 'launch')
    ros2_app_dir = get_package_share_directory('ros2_application')
    bringup_dir = get_package_share_directory('robot_bringup')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    nav2_params_file = os.path.join(bringup_dir, 'config', 'komatsu_nav2_params.yaml')

    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='true')
    autostart_arg = DeclareLaunchArgument('autostart', default_value='true')
    use_localization_arg = DeclareLaunchArgument('use_localization', default_value='true')
    # Default off to avoid map->odom conflicts when Cartographer is launched separately.
    use_mapping_arg = DeclareLaunchArgument('use_mapping', default_value='false')
    use_nav2_arg = DeclareLaunchArgument('use_nav2', default_value='true')
    use_sim_odometry_arg = DeclareLaunchArgument('use_sim_odometry', default_value='false')
    use_sim_imu_arg = DeclareLaunchArgument('use_sim_imu', default_value='false')
    use_sim_scan_arg = DeclareLaunchArgument('use_sim_scan', default_value='false')
    odom_topic_arg = DeclareLaunchArgument('odom_topic', default_value='/odometry/filtered')
    scan_topic_arg = DeclareLaunchArgument('scan_topic', default_value='/scan')
    params_file_arg = DeclareLaunchArgument('params_file', default_value=nav2_params_file)

    x_pose_arg = DeclareLaunchArgument('x_pose', default_value='-24.1')
    y_pose_arg = DeclareLaunchArgument('y_pose', default_value='-11.3')
    z_pose_arg = DeclareLaunchArgument('z_pose', default_value='0.0')

    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    use_localization = LaunchConfiguration('use_localization')
    use_mapping = LaunchConfiguration('use_mapping')
    use_nav2 = LaunchConfiguration('use_nav2')
    use_sim_odometry = LaunchConfiguration('use_sim_odometry')
    use_sim_imu = LaunchConfiguration('use_sim_imu')
    use_sim_scan = LaunchConfiguration('use_sim_scan')
    odom_topic = LaunchConfiguration('odom_topic')
    scan_topic = LaunchConfiguration('scan_topic')
    params_file = LaunchConfiguration('params_file')
    # SW-corner spawn with ~2m clearance to walls (60x30 field), based on nav footprint extents.
    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')
    z_pose = LaunchConfiguration('z_pose')

    world = os.path.join(
        get_package_share_directory('robot_bringup'),
        'worlds',
        'test_field.world'
    )

    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world}.items()
    )

    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        )
    )

    robot_state_publisher_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(my_robot_launch_dir, 'robot_state_publisher.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    spawn_robot_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(my_robot_launch_dir, 'spawn_my_robot.launch.py')
        ),
        launch_arguments={
            'x_pose': x_pose,
            'y_pose': y_pose,
            'z_pose': z_pose,
        }.items()
    )

    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros2_app_dir, 'launch', 'komatsu_localization.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'use_sim_odometry': use_sim_odometry,
            'use_sim_imu': use_sim_imu,
        }.items(),
        condition=IfCondition(use_localization),
    )

    mapping_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros2_app_dir, 'launch', 'komatsu_mapping.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'use_sim_scan': use_sim_scan,
            'odom_topic': odom_topic,
            'scan_topic': scan_topic,
        }.items(),
        condition=IfCondition(use_mapping),
    )

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_dir, 'launch', 'komatsu_nav2.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'params_file': params_file,
        }.items(),
        condition=IfCondition(use_nav2),
    )

    startup_logs = [
        LogInfo(msg=['[Gazebo+Nav2] use_sim_odometry=', use_sim_odometry,
                     ', use_sim_imu=', use_sim_imu,
                     ', use_sim_scan=', use_sim_scan]),
        LogInfo(msg=['[Gazebo+Nav2] use_localization=', use_localization,
                     ', use_mapping=', use_mapping,
                     ', use_nav2=', use_nav2]),
        LogInfo(msg=['[Gazebo+Nav2] odom_topic=', odom_topic,
                     ', scan_topic=', scan_topic]),
    ]

    ld = LaunchDescription()
    ld.add_action(use_sim_time_arg)
    ld.add_action(autostart_arg)
    ld.add_action(use_localization_arg)
    ld.add_action(use_mapping_arg)
    ld.add_action(use_nav2_arg)
    ld.add_action(use_sim_odometry_arg)
    ld.add_action(use_sim_imu_arg)
    ld.add_action(use_sim_scan_arg)
    ld.add_action(odom_topic_arg)
    ld.add_action(scan_topic_arg)
    ld.add_action(params_file_arg)
    ld.add_action(x_pose_arg)
    ld.add_action(y_pose_arg)
    ld.add_action(z_pose_arg)
    for log_action in startup_logs:
        ld.add_action(log_action)
    ld.add_action(gzserver_cmd)
    ld.add_action(gzclient_cmd)
    ld.add_action(robot_state_publisher_cmd)
    ld.add_action(spawn_robot_cmd)
    ld.add_action(localization_launch)
    ld.add_action(mapping_launch)
    ld.add_action(nav2_launch)

    return ld

