from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'ros_ll_controller_python'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools', 'loguru'],
    zip_safe=True,
    maintainer='sellig',
    maintainer_email='gilles.mottiez@syrto.ch',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
                'll_controller = ros_ll_controller_python.controller:main',
        ],
    }
)
