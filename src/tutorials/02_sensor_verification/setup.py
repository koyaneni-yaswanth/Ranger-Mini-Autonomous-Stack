from setuptools import setup
import os

package_name = 'tutorial_sensor_verification'

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
    description='Tutorial 02: Automated Sensor Health and TF Verification for Ranger Mini',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sensor_health_checker = tutorial_sensor_verification.sensor_health_checker:main',
        ],
    },
)
