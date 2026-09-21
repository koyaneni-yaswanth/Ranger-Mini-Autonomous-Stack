import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
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
        
        # EKF Node for Odometry -> Base Footprint TF
        Node(
            package='ranger_control',
            executable='odom_tf_broadcaster.py',
            name='odom_tf_broadcaster',
            output='screen',
            parameters=[{'use_sim_time': True}]
        )
    ])
