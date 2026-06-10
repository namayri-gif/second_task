from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('turtlebot3_obstacle_avoidance'),
        'config', 'params.yaml')

    return LaunchDescription([
        Node(
            package='turtlebot3_obstacle_avoidance',
            executable='obstacle_avoidance_node',
            name='obstacle_avoidance_node',
            output='screen',
            parameters=[config]
        )
    ])
