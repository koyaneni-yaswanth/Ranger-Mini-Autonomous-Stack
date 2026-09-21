from setuptools import setup
import os

package_name = 'tutorial_manipulation_pick_place'

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
    description='Tutorial 04: MoveIt 2 Trajectory Planning and Pick-Place for Piper Arm',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pick_and_place_tutorial = tutorial_manipulation_pick_place.pick_and_place_tutorial:main',
        ],
    },
)
