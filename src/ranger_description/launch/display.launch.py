import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, FindExecutable, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_description = get_package_share_directory('ranger_description')
    urdf_file = os.path.join(pkg_description, 'urdf', 'ranger_mini.urdf.xacro')
    rviz_file = os.path.join(pkg_description, 'rviz', 'description.rviz')

    use_sim_time = LaunchConfiguration('use_sim_time')
    gui = LaunchConfiguration('gui')
    rviz = LaunchConfiguration('rviz')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )
    declare_gui = DeclareLaunchArgument(
        'gui',
        default_value='false',
        description='Flag to enable joint_state_publisher_gui'
    )
    declare_rviz = DeclareLaunchArgument(
        'rviz',
        default_value='false',
        description='Flag to enable RViz'
    )

    robot_description_content = Command(
        [FindExecutable(name='xacro'), ' ', '"', urdf_file, '"']
    )
    robot_description = {'robot_description': ParameterValue(robot_description_content, value_type=str)}

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': use_sim_time}]
    )

    node_joint_state_publisher = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=IfCondition(gui)
    )

    node_rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_file],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
        condition=IfCondition(rviz)
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_gui,
        declare_rviz,
        node_robot_state_publisher,
        node_joint_state_publisher,
        node_rviz
    ])
