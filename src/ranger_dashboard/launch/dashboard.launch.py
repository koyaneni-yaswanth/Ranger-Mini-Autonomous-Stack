import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

# NOTE: You must install these packages:
# sudo apt-get install ros--rosbridge-server ros--web-video-server

def generate_launch_description():
    return LaunchDescription([
        # Rosbridge Server (WebSockets -> ROS 2)
        Node(
            package='rosbridge_server',
            executable='rosbridge_websocket',
            name='rosbridge_websocket',
            output='screen',
            parameters=[{'port': 9090}]
        ),
        # Web Video Server (ROS 2 Images -> HTTP Streams)
        Node(
            package='web_video_server',
            executable='web_video_server',
            name='web_video_server',
            output='screen',
            parameters=[{'port': 8080}]
        )
    ])
