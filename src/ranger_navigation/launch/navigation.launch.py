import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # Get the launch directory
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    ranger_navigation_dir = get_package_share_directory('ranger_navigation')

    # Create the launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(ranger_navigation_dir, 'config', 'nav2_params.yaml'),
        description='Full path to the ROS2 parameters file to use for all launched nodes')

    # Include the Nav2 bringup launch file
    # We will launch localization and navigation. Since we already have a map from SLAM,
    # if we want to run AMCL, we'd provide a map. But if we run SLAM alongside Nav2, 
    # we don't need AMCL (SLAM Toolbox provides odom->map tf).
    # Since we are doing SLAM & Nav at the same time, we only need the navigation core.
    
    navigation_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')),
        launch_arguments={'use_sim_time': use_sim_time,
                          'params_file': params_file}.items())

    # Create the launch description and populate
    ld = LaunchDescription()

    # Declare the launch options
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_params_file_cmd)

    # Add the actions to launch all of the navigation nodes
    ld.add_action(navigation_cmd)

    return ld
