"""Action 6 integration launch: robot model + localization + mapping + Nav2 + RViz."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    """Generate Action 6 RViz integration launch description."""

    ros2_app_dir = get_package_share_directory('ros2_application')
    robot_desc_dir = get_package_share_directory('robot_description')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    bringup_dir = get_package_share_directory('robot_bringup')

    urdf_file = os.path.join(robot_desc_dir, 'urdf', 'komatsu.urdf.xacro')
    nav2_params_file = os.path.join(bringup_dir, 'config', 'komatsu_nav2_params.yaml')
    nav2_rviz_config = os.path.join(nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz')

    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock if available',
    )

    autostart = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically transition Nav2 lifecycle nodes',
    )

    use_sim_odometry = DeclareLaunchArgument(
        'use_sim_odometry',
        default_value='true',
        description='Use simulated odometry source for UKF',
    )

    use_sim_imu = DeclareLaunchArgument(
        'use_sim_imu',
        default_value='true',
        description='Use simulated IMU source for UKF',
    )

    use_sim_scan = DeclareLaunchArgument(
        'use_sim_scan',
        default_value='true',
        description='Use simulated LaserScan source for RTAB-Map',
    )

    use_cmd_vel_joint_sim = DeclareLaunchArgument(
        'use_cmd_vel_joint_sim',
        default_value='true',
        description='Publish wheel/articulation joint states from cmd_vel for RViz animation',
    )

    joint_cmd_topic = DeclareLaunchArgument(
        'joint_cmd_topic',
        default_value='/cmd_vel',
        description='Twist topic used by cmd_vel_joint_state_publisher',
    )

    odom_topic = DeclareLaunchArgument(
        'odom_topic',
        default_value='/odometry/filtered',
        description='Odometry topic for mapping stage',
    )

    scan_topic = DeclareLaunchArgument(
        'scan_topic',
        default_value='/scan',
        description='LaserScan topic for mapping and Nav2 costmaps',
    )

    params_file = DeclareLaunchArgument(
        'params_file',
        default_value=nav2_params_file,
        description='Nav2 params file',
    )

    use_rviz = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Launch RViz for Action 6 verification',
    )

    rviz_config = DeclareLaunchArgument(
        'rviz_config',
        default_value=nav2_rviz_config,
        description='RViz config file',
    )

    robot_description_content = ParameterValue(Command(['xacro ', urdf_file]), value_type=str)

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
    )

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
        condition=UnlessCondition(LaunchConfiguration('use_cmd_vel_joint_sim')),
    )

    cmd_vel_joint_state_publisher = Node(
        package='ros2_application',
        executable='cmd_vel_joint_state_publisher',
        name='cmd_vel_joint_state_publisher',
        output='screen',
        parameters=[{
            'cmd_vel_topic': LaunchConfiguration('joint_cmd_topic'),
            'joint_state_topic': '/joint_states',
            'wheel_radius': 0.8,
            'track_width': 2.16,
            'wheel_base': 3.03,
            'max_articulation_angle': 0.35,
            'max_articulation_rate': 0.175,
        }],
        condition=IfCondition(LaunchConfiguration('use_cmd_vel_joint_sim')),
    )

    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros2_app_dir, 'launch', '../../ros2_application/launch/komatsu_localization.launch.py')
        ),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'use_sim_odometry': LaunchConfiguration('use_sim_odometry'),
            'use_sim_imu': LaunchConfiguration('use_sim_imu'),
        }.items(),
    )

    mapping_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros2_app_dir, 'launch', '../../ros2_application/launch/komatsu_mapping.launch.py')
        ),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'use_sim_scan': LaunchConfiguration('use_sim_scan'),
            'odom_topic': LaunchConfiguration('odom_topic'),
            'scan_topic': LaunchConfiguration('scan_topic'),
        }.items(),
    )

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'autostart': LaunchConfiguration('autostart'),
            'params_file': LaunchConfiguration('params_file'),
        }.items(),
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        condition=IfCondition(LaunchConfiguration('use_rviz')),
    )

    startup_logs = [
        LogInfo(msg=['[Action6] use_sim_odometry=', LaunchConfiguration('use_sim_odometry'),
                     ', use_sim_imu=', LaunchConfiguration('use_sim_imu'),
                     ', use_sim_scan=', LaunchConfiguration('use_sim_scan')]),
        LogInfo(msg=['[Action6] odom_topic=', LaunchConfiguration('odom_topic'),
                     ', scan_topic=', LaunchConfiguration('scan_topic')]),
        LogInfo(msg=['[Action6] Nav2 bringup launches navigation nodes only; '
                     'AMCL/map_server lifecycle is not started in this SLAM flow.']),
    ]

    return LaunchDescription([
        use_sim_time,
        autostart,
        use_sim_odometry,
        use_sim_imu,
        use_sim_scan,
        use_cmd_vel_joint_sim,
        joint_cmd_topic,
        odom_topic,
        scan_topic,
        params_file,
        use_rviz,
        rviz_config,
        *startup_logs,
        robot_state_publisher,
        joint_state_publisher,
        cmd_vel_joint_state_publisher,
        localization_launch,
        mapping_launch,
        nav2_launch,
        rviz_node,
    ])

