from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    autostart = LaunchConfiguration('autostart')

    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    robot_bringup_dir = get_package_share_directory('robot_bringup')

    default_params_file = os.path.join(
        robot_bringup_dir,
        'config',
        'fendt_nav2_params.yaml'
    )

    nav2_launch = os.path.join(
        nav2_bringup_dir,
        'launch',
        'navigation_launch.py'
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
            'autostart',
            default_value='true'
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'params_file': params_file,
                'autostart': autostart
            }.items()
        )
    ])