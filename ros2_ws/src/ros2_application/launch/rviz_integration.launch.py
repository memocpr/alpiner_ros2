"""Action 6 integration launch: robot model + localization + mapping + Nav2 + RViz."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    """Generate Action 6 RViz integration launch description."""

    ros2_app_dir = get_package_share_directory('ros2_application')
    robot_desc_dir = get_package_share_directory('robot_description')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    urdf_file = os.path.join(robot_desc_dir, 'urdf', 'komatsu.urdf.xacro')
    nav2_params_file = os.path.join(nav2_bringup_dir, 'params', 'nav2_params.yaml')
    nav2_rviz_config = os.path.join(nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz')

    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
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
    )

    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros2_app_dir, 'launch', 'localization.launch.py')
        ),
        launch_arguments={
            'use_sim_odometry': LaunchConfiguration('use_sim_odometry'),
            'use_sim_imu': LaunchConfiguration('use_sim_imu'),
        }.items(),
    )

    mapping_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros2_app_dir, 'launch', 'mapping.launch.py')
        ),
        launch_arguments={
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

    return LaunchDescription([
        use_sim_time,
        autostart,
        use_sim_odometry,
        use_sim_imu,
        use_sim_scan,
        odom_topic,
        scan_topic,
        params_file,
        use_rviz,
        rviz_config,
        robot_state_publisher,
        joint_state_publisher,
        localization_launch,
        mapping_launch,
        nav2_launch,
        rviz_node,
    ])

