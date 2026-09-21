import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    publish_odom_tf = LaunchConfiguration('publish_odom_tf')
    declare_publish_odom_tf = DeclareLaunchArgument(
        'publish_odom_tf',
        default_value='false',
        description='Whether to publish odom->base_footprint TF (keep false in simulation to prevent duplicate TF with Gazebo)'
    )

    return LaunchDescription([
        declare_publish_odom_tf,

        # Joint State Broadcaster
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
            output='screen',
        ),
        
        # Steering Controller (Position)
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['steering_controller', '--controller-manager', '/controller_manager'],
            output='screen',
        ),
        
        # Traction Controller (Velocity)
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['traction_controller', '--controller-manager', '/controller_manager'],
            output='screen',
        ),
        
        # Piper Arm Controller
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['piper_arm_controller', '--controller-manager', '/controller_manager'],
            output='screen',
        ),

        # Ranger Kinematics Node
        Node(
            package='ranger_control',
            executable='kinematics_node.py',
            name='ranger_kinematics_node',
            output='screen',
        ),
        
        # Odom TF Broadcaster (only enabled when publish_odom_tf is true)
        Node(
            package='ranger_control',
            executable='odom_tf_broadcaster.py',
            name='odom_tf_broadcaster',
            output='screen',
            parameters=[{'use_sim_time': True}],
            condition=IfCondition(publish_odom_tf)
        )
    ])
