"""Action 7 launch: Gazebo + Localization + Mapping + Nav2 + RViz (all-in-one)."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Generate Action 7 Gazebo + full stack launch."""

    robot_desc_dir = get_package_share_directory('robot_description')
    ros2_app_dir = get_package_share_directory('ros2_application')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    gazebo_ros_dir = get_package_share_directory('gazebo_ros')
    bringup_dir = get_package_share_directory('robot_bringup')

    nav2_params_file = os.path.join(bringup_dir, 'config', 'komatsu_nav2_params.yaml')
    nav2_rviz_config = os.path.join(nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz')

    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time',
    )

    params_file = DeclareLaunchArgument(
        'params_file',
        default_value=nav2_params_file,
        description='Nav2 params file',
    )

    # Gazebo (robot_description/komatsu_gazebo.launch.py)
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(robot_desc_dir, 'launch', 'komatsu_gazebo.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items(),
    )

    # Localization (no sim sources, use Gazebo sensors)
    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros2_app_dir, 'launch', '../../ros2_application/launch/komatsu_localization.launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'use_sim_odometry': 'false',
            'use_sim_imu': 'false',
        }.items(),
    )

    # Mapping (no sim scan, use Gazebo lidar)
    mapping_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros2_app_dir, 'launch', '../../ros2_application/launch/komatsu_mapping.launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'use_sim_scan': 'false',
        }.items(),
    )

    # Nav2
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'params_file': LaunchConfiguration('params_file'),
        }.items(),
    )

    # RViz
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', nav2_rviz_config],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    return LaunchDescription([
        use_sim_time,
        params_file,
        gazebo_launch,
        localization_launch,
        mapping_launch,
        nav2_launch,
        rviz_node,
    ])

