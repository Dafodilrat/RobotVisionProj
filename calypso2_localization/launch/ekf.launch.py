from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


pkg_dir =  get_package_share_directory('calypso2_localization')

start_robot_localization_cmd = Node(
    package='robot_localization',
    executable='ekf_node',
    name='ekf_filter_node',
    output='screen',
    parameters=[pkg_dir+'/config/ekf.yaml', 
    {'use_sim_time': True}])


def generate_launch_description():
    return LaunchDescription([
        start_robot_localization_cmd
    ])