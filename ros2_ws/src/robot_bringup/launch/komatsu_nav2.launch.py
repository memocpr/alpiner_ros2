from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    map_file = LaunchConfiguration('map')
    autostart = LaunchConfiguration('autostart')
    use_sim_scan = LaunchConfiguration('use_sim_scan')

    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    robot_bringup_dir = get_package_share_directory('robot_bringup')

    default_params_file = os.path.join(
        robot_bringup_dir,
        'config',
        'komatsu_nav2_params.yaml'
    )

    default_map_file = os.path.join(
        robot_bringup_dir,
        'maps',
        'map.yaml'
    )

    nav2_launch = os.path.join(
        nav2_bringup_dir,
        'launch',
        'navigation_launch.py'
    )

    sim_scan_node = Node(
        package='ros2_application',
        executable='sim_scan_publisher',
        name='sim_scan',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
        }],
        condition=IfCondition(use_sim_scan),
    )

    sim_scan_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='sim_scan_static_tf',
        arguments=['0.0', '0.0', '1.0', '0.0', '0.0', '0.0', 'base_link', 'laser_frame'],
        parameters=[{
            'use_sim_time': use_sim_time,
        }],
        condition=IfCondition(use_sim_scan),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false'
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params_file
        ),
        DeclareLaunchArgument(
            'map',
            default_value=default_map_file
        ),
        DeclareLaunchArgument(
            'autostart',
            default_value='true'
        ),
        DeclareLaunchArgument(
            'use_sim_scan',
            default_value='true'
        ),
        sim_scan_node,
        sim_scan_tf,
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'params_file': params_file,
                'map': map_file,
                'autostart': autostart
            }.items()
        )
    ])