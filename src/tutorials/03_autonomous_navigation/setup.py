from setuptools import setup
import os

package_name = 'tutorial_autonomous_navigation'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Ranger Mini Autonomy Team',
    maintainer_email='dev@ranger-mini.org',
    description='Tutorial 03: Waypoint Dispatch and Nav2 Autonomous Missions for Ranger Mini',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'waypoint_navigator = tutorial_autonomous_navigation.waypoint_navigator:main',
        ],
    },
)
