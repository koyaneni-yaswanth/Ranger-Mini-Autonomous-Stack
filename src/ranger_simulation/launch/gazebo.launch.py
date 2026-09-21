import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def launch_setup(context, *args, **kwargs):
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_simulation = get_package_share_directory('ranger_simulation')
    pkg_description = get_package_share_directory('ranger_description')

    world_name = LaunchConfiguration('world').perform(context)
    world_file = os.path.join(pkg_simulation, 'worlds', world_name)
    headless = LaunchConfiguration('headless').perform(context).lower() == 'true'

    if headless or not os.environ.get('DISPLAY'):
        gz_args = f"-s -r {world_file}"
    else:
        gz_args = f"-r --render-engine ogre {world_file}"

    # Gazebo Environment Variables for resource path
    set_ign_env = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=f"{os.path.join(pkg_description, '..')}:{os.path.join(pkg_simulation, 'worlds')}"
    )
    set_gz_env = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=f"{os.path.join(pkg_description, '..')}:{os.path.join(pkg_simulation, 'worlds')}"
    )
    set_ign_plugin = SetEnvironmentVariable(
        name='IGN_GAZEBO_SYSTEM_PLUGIN_PATH',
        value='/opt/ros/humble/lib'
    )
    set_gz_plugin = SetEnvironmentVariable(
        name='GZ_SIM_SYSTEM_PLUGIN_PATH',
        value='/opt/ros/humble/lib'
    )
    set_adapter = SetEnvironmentVariable(
        name='MESA_D3D12_DEFAULT_ADAPTER_NAME',
        value='NVIDIA'
    )

    # Launch Gazebo server and client
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': gz_args}.items()
    )

    # Spawn the Ranger Mini from the ROS topic
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'ranger_mini',
            '-z', '0.2'
        ],
        output='screen'
    )

    # Include the display launch (runs robot_state_publisher with use_sim_time=true, gui=false, rviz=false)
    description = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_description, 'launch', 'display.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true', 'gui': 'false', 'rviz': 'false'}.items()
    )

    # The ROS-GZ Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/model/ranger_mini/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
            '/odometry@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/lidar/points/points@sensor_msgs/msg/PointCloud2[ignition.msgs.PointCloudPacked',
            '/camera/image@sensor_msgs/msg/Image[ignition.msgs.Image',
            '/camera/depth_image@sensor_msgs/msg/Image[ignition.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[ignition.msgs.CameraInfo',
            '/imu@sensor_msgs/msg/Imu[ignition.msgs.IMU',
            '/gps/fix@sensor_msgs/msg/NavSatFix[ignition.msgs.NavSat'
        ],
        remappings=[
            ('/model/ranger_mini/tf', '/tf'),
            ('/odometry', '/odom'),
            ('/lidar/points/points', '/lidar/points'),
            ('/camera/image', '/camera'),
        ],
        output='screen'
    )

    # Control Launch
    control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ranger_control'), 'launch', 'control.launch.py')
        ])
    )

    # Sensor Processing Launch
    perception_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ranger_perception'), 'launch', 'sensor_processing.launch.py')
        ])
    )

    # SLAM Launch
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ranger_slam'), 'launch', 'mapping.launch.py')
        ])
    )

    # Navigation2 Launch
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ranger_navigation'), 'launch', 'navigation.launch.py')
        ])
    )

    # Vision & AI Launch
    vision_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ranger_vision'), 'launch', 'vision.launch.py')
        ])
    )

    return [
        set_ign_env,
        set_gz_env,
        set_ign_plugin,
        set_gz_plugin,
        set_adapter,
        gazebo,
        description,
        spawn_robot,
        bridge,
        control_launch,
        perception_launch,
        slam_launch,
        nav2_launch,
        vision_launch
    ]

def generate_launch_description():
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='warehouse.sdf',
        description='Simulation world to load'
    )
    headless_arg = DeclareLaunchArgument(
        'headless',
        default_value='false' if os.environ.get('DISPLAY') else 'true',
        description='Run Gazebo headless (-s) if true'
    )

    return LaunchDescription([
        world_arg,
        headless_arg,
        OpaqueFunction(function=launch_setup)
    ])
