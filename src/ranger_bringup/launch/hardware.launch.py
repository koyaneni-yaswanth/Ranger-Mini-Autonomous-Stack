import os
from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_bringup = get_package_share_directory('ranger_bringup')
    pkg_description = get_package_share_directory('ranger_description')
    
    can_interface_arg = DeclareLaunchArgument(
        'can_interface',
        default_value='can0',
        description='SocketCAN interface name'
    )
    
    can_interface = LaunchConfiguration('can_interface')

    # 1. Robot State Publisher (URDF)
    description = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_description, 'launch', 'display.launch.py')
        ),
        launch_arguments={'use_sim_time': 'false'}.items()
    )

    # 2. AgileX Ranger Mini Base Hardware Driver
    base_driver = Node(
        package='ranger_base',
        executable='ranger_base_node',
        name='ranger_base_node',
        output='screen',
        parameters=[{
            'port_name': can_interface,
            'robot_model': 'ranger_mini_v2',
            'update_rate': 50,
            'odom_frame': 'odom',
            'base_frame': 'base_footprint'
        }]
    )

    actions = [
        can_interface_arg,
        description
    ]

    # 3. Optional Livox Mid-360 LiDAR Hardware Driver
    try:
        livox_pkg = get_package_share_directory('livox_ros_driver2')
        livox_driver = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(livox_pkg, 'launch_ROS2', 'msg_MID360_launch.py')
            )
        )
        actions.append(livox_driver)
    except (PackageNotFoundError, LookupError):
        pass
    
    # 4. Optional Intel RealSense Hardware Driver
    try:
        realsense_pkg = get_package_share_directory('realsense2_camera')
        realsense_driver = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(realsense_pkg, 'launch', 'rs_launch.py')
            ),
            launch_arguments={
                'enable_depth': 'true',
                'enable_color': 'true',
                'pointcloud.enable': 'false',
                'rgb_camera.profile': '640x480x30'
            }.items()
        )
        actions.append(realsense_driver)
    except (PackageNotFoundError, LookupError):
        pass

    # 5. EKF Sensor Fusion (Odom + IMU)
    ekf_config = os.path.join(pkg_bringup, 'config', 'ekf_hardware.yaml')
    if os.path.exists(ekf_config):
        ekf_node = Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[ekf_config]
        )
        actions.append(ekf_node)

    # 6. Perception (Pointcloud to LaserScan)
    try:
        perc_pkg = get_package_share_directory('ranger_perception')
        perception_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(perc_pkg, 'launch', 'sensor_processing.launch.py')
            ),
            launch_arguments={'use_sim_time': 'false'}.items()
        )
        actions.append(perception_launch)
    except (PackageNotFoundError, LookupError):
        pass

    # 7. Navigation Stack (Nav2 + SLAM)
    try:
        nav_pkg = get_package_share_directory('ranger_navigation')
        nav2_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav_pkg, 'launch', 'navigation.launch.py')
            ),
            launch_arguments={'use_sim_time': 'false'}.items()
        )
        actions.append(nav2_launch)
    except (PackageNotFoundError, LookupError):
        pass
    
    try:
        slam_pkg = get_package_share_directory('ranger_slam')
        slam_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(slam_pkg, 'launch', 'mapping.launch.py')
            ),
            launch_arguments={'use_sim_time': 'false'}.items()
        )
        actions.append(slam_launch)
    except (PackageNotFoundError, LookupError):
        pass

    return LaunchDescription(actions)
