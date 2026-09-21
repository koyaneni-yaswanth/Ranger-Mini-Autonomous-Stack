from setuptools import setup
import os
from glob import glob

package_name = 'tutorial_basic_teleop'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Ranger Mini Autonomy Team',
    maintainer_email='dev@ranger-mini.org',
    description='Tutorial 01: Basic Teleoperation, Kinematics and Twist MUX for Ranger Mini',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'teleop_supervisor = tutorial_basic_teleop.teleop_supervisor:main',
        ],
    },
)
