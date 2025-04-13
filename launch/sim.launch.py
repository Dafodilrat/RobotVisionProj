import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution, LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    package_name = 'calypso2'
    package_path = get_package_share_directory(package_name)
    
    # Path to Xacro file
    xacro_file = os.path.join(package_path, 'urdf', 'auv.urdf.xacro')

    # Convert Xacro to URDF dynamically
    robot_description = ParameterValue(
        Command(['xacro', xacro_file]), value_type=str
    )


    urdf = IncludeLaunchDescription(
        PathJoinSubstitution([FindPackageShare('urdf_launch'), 'launch', 'display.launch.py']),
        launch_arguments={
            'urdf_package': package_name,
            'urdf_package_path': PathJoinSubstitution(['urdf', LaunchConfiguration('model')]),
    )
    # Spawn Robot in Gazebo
    spawn_urdf_node = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name", "auv",
            "-topic", "robot_description",
            "-x", "0.0", "-y", "0.0", "-z", "0.5", "-Y", "0.0"  # Initial spawn position
        ],
        output="screen",
        parameters=[
            {'use_sim_time': True},
        ]
    )


    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        spawn_urdf_node,
        robot_state_publisher,
        spawn_robot
    ])
