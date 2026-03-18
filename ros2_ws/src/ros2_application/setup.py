from glob import glob
from setuptools import find_packages, setup

package_name = 'ros2_application'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', [
            'config/ukf_params.yaml',
            'config/rtabmap_params.yaml',
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='evomrx22',
    maintainer_email='mehmetcopur_01@outlook.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'sim_odometry_publisher = ros2_application.sim_odometry_publisher:main',
            'sim_imu_publisher = ros2_application.sim_imu_publisher:main',
            'sim_scan_publisher = ros2_application.sim_scan_publisher:main',
            'cmd_vel_joint_state_publisher = ros2_application.cmd_vel_joint_state_publisher:main',
            'send_nav_goal = ros2_application.send_nav_goal:main',
            'sim_gnss_publisher = ros2_application.sim_gnss_publisher:main',
        ],
    },
)
