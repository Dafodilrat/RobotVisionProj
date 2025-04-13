import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import  LaunchConfiguration, PathJoinSubstitution, TextSubstitution
from launch_ros.actions import Node
def generate_launch_description():

    pkg_dir = get_package_share_directory('calypso2')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    world_arg = DeclareLaunchArgument(
        'world', default_value=pkg_dir+'/world/'+'empty.sdf',
        description='Name of the Gazebo world file to load'
    )

    # gazebo_launch = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py'),
    #     ),
    #     launch_arguments={'gz_args': [PathJoinSubstitution([
    #         pkg_dir,
    #         'world',
    #         LaunchConfiguration('world')
    #     ]),
    #     # TextSubstitution(text=' -r -v -v1 --render-engine ogre')
    #     ],
    #     # TextSubstitution(text=' -r -v -v1')],
    #     'on_exit_shutdown': 'true'}.items()
    # )

    gazebo_launch = ExecuteProcess(
            cmd=['ign', 'gazebo', pkg_dir+'/world/'+'empty.sdf', '--force-version', '6'],
            output='screen'
        )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    launchDescriptionObject = LaunchDescription()

    launchDescriptionObject.add_action(bridge)
    launchDescriptionObject.add_action(world_arg)
    launchDescriptionObject.add_action(gazebo_launch)

    return launchDescriptionObject