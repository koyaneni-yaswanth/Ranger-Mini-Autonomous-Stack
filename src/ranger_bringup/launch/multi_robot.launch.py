import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import PushRosNamespace

def generate_launch_description():
    pkg_sim = get_package_share_directory('ranger_simulation')
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_sim, 'launch', 'empty_world.launch.py')
        )
    )
    
    # Spawn Robot 1
    robot_1 = GroupAction([
        PushRosNamespace('robot_1'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_sim, 'launch', 'spawn_robot.launch.py')
            ),
            launch_arguments={'robot_name': 'robot_1', 'x': '0.0', 'y': '0.0'}.items()
        )
    ])
    
    # Spawn Robot 2
    robot_2 = GroupAction([
        PushRosNamespace('robot_2'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_sim, 'launch', 'spawn_robot.launch.py')
            ),
            launch_arguments={'robot_name': 'robot_2', 'x': '2.0', 'y': '2.0'}.items()
        )
    ])

    return LaunchDescription([
        gazebo,
        robot_1,
        robot_2
    ])
