import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_simulation = get_package_share_directory('ranger_simulation')
    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='warehouse.sdf'),
        DeclareLaunchArgument('headless', default_value='false'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_simulation, 'launch', 'gazebo.launch.py')
            ),
            launch_arguments={
                'world': LaunchConfiguration('world'),
                'headless': LaunchConfiguration('headless')
            }.items()
        )
    ])
