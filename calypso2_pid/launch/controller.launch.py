from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

controller_launch = os.path.join(
    get_package_share_directory('calypso2_localization'),
    'launch',
    'ekf.launch.py'
)

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='calypso2_pid',
            executable='calypso2_pid_controller',
            name='calypso2_controller',
            output='screen',
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(controller_launch))
    
    ])
