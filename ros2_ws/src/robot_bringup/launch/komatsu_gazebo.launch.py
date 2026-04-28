#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, LogInfo, TimerAction, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    bringup_dir = get_package_share_directory('robot_bringup')
    robot_desc_dir = get_package_share_directory('robot_description')
    ros2_app_dir = get_package_share_directory('ros2_application')
    gazebo_dir = get_package_share_directory('gazebo_ros')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    params_file = LaunchConfiguration('params_file')
    enable_rviz = LaunchConfiguration('enable_rviz')
    localization_start_delay = LaunchConfiguration('localization_start_delay')
    ll_chain_start_delay = LaunchConfiguration('ll_chain_start_delay')
    nav2_start_delay = LaunchConfiguration('nav2_start_delay')
    use_ll_control_chain = LaunchConfiguration('use_ll_control_chain')
    atcom_ns = LaunchConfiguration('atcom_ns')

    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')
    z_pose = LaunchConfiguration('z_pose')

    world = os.path.join(
        bringup_dir,
        'worlds',
        'simple_world',
        'field.sdf'
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
            os.path.join(robot_desc_dir, 'launch', 'komatsu', 'robot_state_publisher.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time
        }.items()
    )

    spawn_robot_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(robot_desc_dir, 'launch', 'komatsu', 'spawn_my_robot.launch.py')
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
        'localization_gnss.launch.py'
    )

    localization_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            localization_launch_file
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'use_global_localization': 'true',
        }.items()
    )

    localization_include_log = LogInfo(
        msg=[
            'Including localization launch: ',
            localization_launch_file,
            ' in GPS-only mode (GNSS enabled).',
        ]
    )

    gnss_enabled_log = LogInfo(
        msg='GPS-only navigation ENABLED: GNSS localization ON, dynamic TF map->odom from UKF/navsat, no static map.',
    )

    mapviz_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros2_app_dir, 'launch', 'mapviz.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'use_global_localization': 'true',
        }.items(),
    )

    nav2_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_dir, 'launch', 'robot_nav2.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': params_file,
            'autostart': autostart,
        }.items(),
    )

    ll_controller_cmd = Node(
        package='ros_ll_controller_python',
        executable='ll_controller',
        name='ll_controller_python',
        output='screen',
        namespace=atcom_ns,
        parameters=[
            {'p_gain_braking_ll_controller': 0.5},
            {'factor_throttle_reduction_when_not_active_braking': 0.5},
            {'p_gain_linear_speed_ll_controller': 1.0},
            {'p_gain_angular_speed_ll_controller': 0.14},
            {'i_gain_linear_speed_ll_controller': 0.0},
            {'i_gain_angular_speed_ll_controller': 0.0},
            {'d_gain_linear_speed_ll_controller': 0.0},
            {'d_gain_angular_speed_ll_controller': 0.0},
            {'min_target_angular_speed_ll_controller': 0.0},
            {'cmd_input_topic': '/cmd_vel_nav'},
            {'teleop_input_topic': '/cmd_vel_teleop'},
            {'allow_neutral_shift_on_brake': False},
            {'cmd_vel_timeout_sec': 0.6},
        ],
        respawn=True,
        condition=IfCondition(use_ll_control_chain),
    )

    gazebo_machine_bridge_cmd = Node(
        package='ros2_application',
        executable='gazebo_machine_bridge',
        name='gazebo_machine_bridge',
        output='screen',
        parameters=[
            {'wheel_cmd_topic': '/wheel_velocity_controller/commands'},
            {'articulation_cmd_topic': '/articulation_position_controller/commands'},
            {'wheel_radius_m': 0.8},
            {'wheel_speed_command_scale': 35.0},
            {'odom_topic': '/odom'},
            {'max_forward_speed_mps': 5.0},
            {'max_reverse_speed_mps': 1.0},
            {'throttle_accel_mps2': 0.9},
            {'max_brake_decel_mps2': 1.2},
            {'max_articulation_angle_deg': 32.0},
            {'max_articulation_rate_degps': 20.0},
        ],
        condition=IfCondition(use_ll_control_chain),
    )

    joint_state_broadcaster_spawner_cmd = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager', '/controller_manager',
            '--controller-manager-timeout', '120',
            '--service-call-timeout', '120',
            '--switch-timeout', '120',
        ],
        output='screen',
        condition=IfCondition(use_ll_control_chain),
    )

    wheel_velocity_controller_spawner_cmd = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'wheel_velocity_controller',
            '--controller-manager', '/controller_manager',
            '--controller-manager-timeout', '120',
            '--service-call-timeout', '120',
            '--switch-timeout', '120',
        ],
        output='screen',
        condition=IfCondition(use_ll_control_chain),
    )

    articulation_position_controller_spawner_cmd = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'articulation_position_controller',
            '--controller-manager', '/controller_manager',
            '--controller-manager-timeout', '120',
            '--service-call-timeout', '120',
            '--switch-timeout', '120',
        ],
        output='screen',
        condition=IfCondition(use_ll_control_chain),
    )

    rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', default_rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(enable_rviz),
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
            'enable_rviz',
            default_value='false',
            description='Launch RViz support alongside bringup'
        ),
        DeclareLaunchArgument(
            'localization_start_delay',
            default_value='5.0',
            description='Delay (s) before starting GNSS localization nodes'
        ),
        DeclareLaunchArgument(
            'll_chain_start_delay',
            default_value='3.0',
            description='Delay (s) before starting LL controller + Gazebo bridge'
        ),
        DeclareLaunchArgument(
            'nav2_start_delay',
            default_value='8.0',
            description='Delay (s) before starting mapviz and Nav2 nodes'
        ),
        DeclareLaunchArgument(
            'use_ll_control_chain',
            default_value='true',
            description='Run Nav2 -> LL controller -> Gazebo bridge command path'
        ),
        DeclareLaunchArgument(
            'atcom_ns',
            default_value='atcom_wa380',
            description='Namespace for LL controller node name'
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params_file
        ),
        DeclareLaunchArgument(
            'x_pose',
            default_value='-124.0'
        ),
        DeclareLaunchArgument(
            'y_pose',
            default_value='-70.0'
        ),
        DeclareLaunchArgument(
            'z_pose',
            default_value='0.0'
        ),
        SetEnvironmentVariable('FASTDDS_BUILTIN_TRANSPORTS', 'UDPv4'),
        gzserver_cmd,
        gzclient_cmd,
        robot_state_publisher_cmd,
        spawn_robot_cmd,
        TimerAction(
            period=localization_start_delay,
            actions=[
                localization_include_log,
                gnss_enabled_log,
                localization_cmd,
            ],
        ),
        TimerAction(
            period=ll_chain_start_delay,
            actions=[
                joint_state_broadcaster_spawner_cmd,
                wheel_velocity_controller_spawner_cmd,
                articulation_position_controller_spawner_cmd,
                ll_controller_cmd,
                gazebo_machine_bridge_cmd,
            ],
        ),
        TimerAction(
            period=nav2_start_delay,
            actions=[
                mapviz_cmd,
                nav2_cmd,
            ],
        ),
        rviz_cmd,
    ])