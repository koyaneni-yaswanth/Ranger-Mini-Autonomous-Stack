import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro

from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, FindExecutable

def generate_launch_description():
    # Get URDF and SRDF
    urdf_path = os.path.join(get_package_share_directory('ranger_description'), 'urdf', 'ranger_mini.urdf.xacro')
    srdf_path = os.path.join(get_package_share_directory('ranger_manipulation'), 'config', 'ranger_piper.srdf')
    
    # Process Xacro using Command
    robot_description_content = Command(
        [FindExecutable(name='xacro'), ' ', '"', urdf_path, '"']
    )
    robot_description = {'robot_description': ParameterValue(robot_description_content, value_type=str)}
    
    # Read SRDF
    with open(srdf_path, 'r') as f:
        semantic_content = f.read()
    robot_description_semantic = {'robot_description_semantic': ParameterValue(semantic_content, value_type=str)}

    # Kinematics yaml
    kinematics_path = os.path.join(get_package_share_directory('ranger_manipulation'), 'config', 'kinematics.yaml')
    import yaml
    with open(kinematics_path, 'r') as f:
        kinematics_yaml = yaml.safe_load(f)
    robot_description_kinematics = {'robot_description_kinematics': kinematics_yaml}

    # Controllers yaml
    controllers_path = os.path.join(get_package_share_directory('ranger_manipulation'), 'config', 'moveit_controllers.yaml')
    with open(controllers_path, 'r') as f:
        moveit_controllers = yaml.safe_load(f)

    # MoveGroup Node
    run_move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            robot_description,
            robot_description_semantic,
            robot_description_kinematics,
            {'moveit_controller_manager': 'moveit_simple_controller_manager/MoveItSimpleControllerManager'},
            {'publish_robot_description_semantic': True},
            {'use_sim_time': False},
            moveit_controllers,
        ],
    )

    # Robot State Publisher
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': False}]
    )

    # Joint State Publisher GUI (Fake joints for MoveIt visualization)
    jsp_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        parameters=[robot_description]
    )

    # RViz Config
    rviz_config = os.path.join(get_package_share_directory('ranger_description'), 'rviz', 'description.rviz')

    # RViz with MoveIt Plugin
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[
            robot_description,
            robot_description_semantic,
            {'use_sim_time': False}
        ],
    )

    return LaunchDescription([
        rsp_node,
        jsp_node,
        run_move_group_node,
        rviz_node
    ])
