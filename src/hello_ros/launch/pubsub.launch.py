from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    rate = LaunchConfiguration('rate_hz')
    return LaunchDescription([
        DeclareLaunchArgument('rate_hz', default_value='2.0'),
        Node(package='hello_ros', executable='talker', name='talker',
             parameters=[{'rate_hz': rate}], output='screen'),
        Node(package='hello_ros', executable='listener', name='listener',
             output='screen'),
    ])
