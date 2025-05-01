from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='calypso2_thruster',  # 🔁 Replace this with your actual package name
            executable='pwm_rpm_converter',  # 🔁 This should match the entry point from setup.py
            output='screen'
        )
    ])