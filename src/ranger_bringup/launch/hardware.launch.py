import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_bringup = get_package_share_directory('ranger_bringup')
    pkg_description = get_package_share_directory('ranger_description')
    
    # 1. Robot State Publisher (URDF)
    description = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_description, 'launch', 'display.launch.py')
        ),
        launch_arguments={'use_sim_time': 'false'}.items()
    )

    # 2. AgileX Ranger Mini Base Hardware Driver
    # (Assuming you have standard ugv_sdk or ranger_ros2 installed on the DevKit)
    base_driver = Node(
        package='ranger_base',
        executable='ranger_base_node',
        name='ranger_base_node',
        output='screen',
        parameters=[{
            'port_name': 'can0',
            'robot_model': 'ranger_mini_v2',
            'update_rate': 50,
            'odom_frame': 'odom',
            'base_frame': 'base_footprint'
        }]
    )

    # 3. Livox Mid-360 LiDAR Hardware Driver
    livox_driver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('livox_ros_driver2'), 'launch_ROS2', 'msg_MID360_launch.py')
        ])
    )
    
    # 4. Intel RealSense Hardware Driver
    realsense_driver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('realsense2_camera'), 'launch', 'rs_launch.py')
        ]),
        launch_arguments={
            'enable_depth': 'true',
            'enable_color': 'true',
            'pointcloud.enable': 'false', # We use Livox for pointclouds
            'rgb_camera.profile': '640x480x30'
        }.items()
    )

    # 5. EKF Sensor Fusion (Odom + IMU)
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[os.path.join(pkg_bringup, 'config', 'ekf_hardware.yaml')]
    )

    # 6. Perception (Pointcloud to LaserScan)
    perception_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ranger_perception'), 'launch', 'sensor_processing.launch.py')
        ]),
        launch_arguments={'use_sim_time': 'false'}.items()
    )

    # 7. Navigation Stack (Nav2 + SLAM)
    # You can launch mapping or navigation separately, but here is Nav2:
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ranger_navigation'), 'launch', 'navigation.launch.py')
        ]),
        launch_arguments={'use_sim_time': 'false'}.items()
    )
    
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ranger_slam'), 'launch', 'mapping.launch.py')
        ]),
        launch_arguments={'use_sim_time': 'false'}.items()
    )

    return LaunchDescription([
        description,
        # base_driver,      # Uncomment these when on the real robot
        # livox_driver,     # Uncomment these when on the real robot
        # realsense_driver, # Uncomment these when on the real robot
        ekf_node,
        perception_launch,
        slam_launch,
        nav2_launch
    ])
