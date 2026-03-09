from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    map_file = LaunchConfiguration('map')

    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    robot_bringup_dir = get_package_share_directory('robot_bringup')

    default_params_file = os.path.join(
        robot_bringup_dir,
        'config',
        'nav2_params.yaml'
    )

    default_map_file = os.path.join(
        robot_bringup_dir,
        'maps',
        'map.yaml'
    )

    nav2_launch = os.path.join(
        nav2_bringup_dir,
        'launch',
        'bringup_launch.py'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true'
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params_file
        ),
        DeclareLaunchArgument(
            'map',
            default_value=default_map_file
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'params_file': params_file,
                'map': map_file
            }.items()
        )
    ])