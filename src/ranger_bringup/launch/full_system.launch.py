import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Directories
    pkg_sim = get_package_share_directory('ranger_simulation')
    pkg_nav = get_package_share_directory('ranger_navigation')
    pkg_moveit = get_package_share_directory('ranger_manipulation')
    pkg_perception = get_package_share_directory('ranger_perception')

    # 1. Gazebo + Robot Spawn + Nav2 + Sensors
    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_sim, 'launch', 'gazebo.launch.py')
        )
    )

    # 2. Manipulation
    moveit = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_moveit, 'launch', 'moveit.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # 3. AMR-X Intelligence Layer
    world_model = Node(
        package='amr_world_model',
        executable='semantic_world_model',
        name='semantic_world_model',
        output='screen'
    )

    fleet_manager = Node(
        package='amr_fleet_manager',
        executable='fleet_manager',
        name='fleet_manager',
        output='screen'
    )

    active_perception = Node(
        package='amr_active_perception',
        executable='active_perception',
        name='active_perception',
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        gazebo_sim,
        TimerAction(period=8.0, actions=[moveit]),
        world_model,
        fleet_manager,
        active_perception
    ])
