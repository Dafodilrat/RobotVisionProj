import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import TextSubstitution,Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro

def generate_launch_description():
    
    pkg_dir =  get_package_share_directory('calypso2')

    # Show joint state publisher GUI for joints
    use_sim_time = LaunchConfiguration('use_sim_time', default=True)
    gz_args = LaunchConfiguration('gz_args', default='')


    # URDF model path within the bme_gazebo_basics package
    xacro_file = os.path.join(pkg_dir, 'urdf', 'auv.urdf.xacro')

    controller_config = os.path.join(pkg_dir, 'config', 'controllers.yaml')
    print(type(controller_config))
    print("Exists?", os.path.isfile(controller_config))
 
    robot_description_config = xacro.process_file(xacro_file,mappings={'controller_config_path': controller_config})
    robot_description = robot_description_config.toxml()

    # Use built-in ROS2 URDF launch package with our own arguments
    spawn_robot = ExecuteProcess(
        cmd=[
            'ros2', 'run', 'ros_gz_sim', 'create',
            '-name', 'auv',
            '-topic', '/robot_description',
            '-x', '0',
            '-y', '0',
            '-z', '1'
        ],
        output='screen'
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen'
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
    )
    joint_velocity_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'thruster_velocity_controller',
            '--param-file',
            controller_config,
            ],
    )

    launch_args=DeclareLaunchArgument(
        'use_sim_time',
        default_value=use_sim_time,
        description='If true, use simulated clock'
    )

    gz_sim_launcher= IncludeLaunchDescription(PythonLaunchDescriptionSource(
        [PathJoinSubstitution([FindPackageShare('ros_gz_sim'),
                                       'launch',
                                       'gz_sim.launch.py'])]),
            launch_arguments={'gz_args': TextSubstitution(text=f'-r -v 1 {pkg_dir}/world/empty.sdf')
        }.items())
    
    params_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/imu/data@sensor_msgs/msg/Imu@ignition.msgs.IMU',
            '/world/empty/pose/info@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
            '/world/empty/dynamic_pose/info@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V'
        ],
        output='screen'
    )

    ground_truth= Node(
        package='calypso2',
        executable='calypso2_ground_truth',
        name='calypso2_ground_truth',
        output='screen'
    )

    static_tf_world_to_base = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_world_to_base_link',
        arguments=['0', '0', '0', '0', '0', '0', 'world', 'base_link'],
        output='screen'
    )

    
    return LaunchDescription([
        gz_sim_launcher,
        params_bridge,
        robot_state_publisher,
        joint_state_broadcaster_spawner,
        joint_velocity_controller_spawner,
        launch_args,
        spawn_robot,
        static_tf_world_to_base,
        ground_truth,
    ])