"""Action 7 launch: Gazebo-only bringup for the split-terminal workflow."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    """Generate Gazebo-only launch description for Action 7 Terminal 1."""

    bringup_dir = get_package_share_directory('robot_bringup')
    robot_desc_dir = get_package_share_directory('robot_description')
    gazebo_ros_dir = get_package_share_directory('gazebo_ros')

    urdf_file = os.path.join(robot_desc_dir, 'urdf', 'komatsu_gazebo.urdf.xacro')
    default_world = os.path.join(bringup_dir, 'worlds', 'test_field.world')

    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock',
    )

    world = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description='Absolute path to Gazebo world file',
    )

    robot_description_content = ParameterValue(
        Command(['xacro ', urdf_file]),
        value_type=str,
    )

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

    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_dir, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={
            'world': LaunchConfiguration('world'),
        }.items(),
    )

    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_dir, 'launch', 'gzclient.launch.py')
        ),
    )

    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'komatsu', '-topic', 'robot_description'],
        output='screen',
    )

    return LaunchDescription([
        use_sim_time,
        world,
        robot_state_publisher,
        joint_state_publisher,
        gazebo_server,
        gazebo_client,
        spawn_robot,
    ])
