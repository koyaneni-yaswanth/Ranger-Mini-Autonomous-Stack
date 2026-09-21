import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_sim = get_package_share_directory('ranger_simulation')

    world_arg = DeclareLaunchArgument(
        'world',
        default_value='warehouse.sdf',
        description='Simulation world to load'
    )
    headless_arg = DeclareLaunchArgument(
        'headless',
        default_value='false' if os.environ.get('DISPLAY') else 'true',
        description='Run Gazebo headless'
    )

    simulation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_sim, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': LaunchConfiguration('world'),
            'headless': LaunchConfiguration('headless')
        }.items()
    )

    return LaunchDescription([
        world_arg,
        headless_arg,
        simulation_launch
    ])
