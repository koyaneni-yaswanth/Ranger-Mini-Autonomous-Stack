import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock if true'),
        Node(
            package='pointcloud_to_laserscan',
            executable='pointcloud_to_laserscan_node',
            name='pointcloud_to_laserscan',
            remappings=[
                ('cloud_in', '/lidar/points'),
                ('scan', '/scan')
            ],
            parameters=[{
                'target_frame': 'lidar_link',
                'transform_tolerance': 0.2,
                'min_height': -0.1,
                'max_height': 1.0,
                'angle_min': -3.14159,
                'angle_max': 3.14159,
                'angle_increment': 0.0087,
                'scan_time': 0.1,
                'range_min': 0.2,
                'range_max': 40.0,
                'use_inf': True,
                'inf_epsilon': 1.0,
                'use_sim_time': LaunchConfiguration('use_sim_time')
            }],
            output='screen'
        )
    ])
