import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.event_handlers import on_execution_complete
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # 1. Path definitions
    pkg_description = get_package_share_directory('exoskeleton_description')

    # Evaluate Xacro -> URDF in memory (Used by robot_state_publisher for TF2 and RViz)
    robot_description_content = Command([
        PathJoinSubstitution([FindExecutable(name="xacro")]),
        " ",
        PathJoinSubstitution([FindPackageShare("exoskeleton_description"), "urdf", "exoskeleton.urdf.xacro"])
    ])
    robot_description = {"robot_description": robot_description_content}

    # 2. Robot state publisher node (TF2 Tree Broadcaster for RViz)
    node_robot_state_publisher = Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            output="screen",
            parameters=[robot_description],
    )

    # 3. MuJoCo ROS2 Control Node (Physics Backend)
    # Using the pre-compiled test.xml for exact 6-bar linkage equality constraints
    mujoco_control_node = Node(
            package="mujoco_ros2_control",
            executable="mujoco_control_node",
            output="screen",
            parameters=[
                robot_description,
                {
                    "mujoco_model": os.path.join(pkg_description, "urdf", "test.xml"),
                    "publish_tf": True
                }
            ],
    )

    # 4. Controller Spawners
    joint_state_broadcaster_spawner = Node(
            package="controller_manager",
            executable="spawner",
            arguments=["joint_state_broadcaster", "--controller_manager", "/controller_manager"],
    )

    effort_controller_spawner = Node(
            package="controller_manager",
            executable="spawner",
            arguments=["forward_effort_controller", "--controller_manager", "/controller_manager"],
            )

    # 5. RViz Visualization Node
    rviz_node = Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=["-d", os.path.join(pkg_description, "rviz", "exoskeleton_sim.rviz")],
            )

    return LaunchDescription([
        node_robot_state_publisher,
        mujoco_control_node,
        joint_state_broadcaster_spawner,
        effort_controller_spawner,
        rviz_node,
        ])

