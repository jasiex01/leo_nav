
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, EmitEvent, LogInfo,
                            RegisterEventHandler)
from launch.events import matches_action
from launch.substitutions import (LaunchConfiguration)
from launch_ros.actions import LifecycleNode
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition


def generate_launch_description():
    slam_params_file = LaunchConfiguration('slam_params_file')
    map_file_name = LaunchConfiguration('map_file_name')

    declare_slam_params_file_cmd = DeclareLaunchArgument(
        'slam_params_file',
        default_value=os.path.join(get_package_share_directory("leo_nav"),
                                   'config', 'slam_toolbox_localization_config.yaml'),
        description='Full path to the ROS2 parameters file to use for the slam_toolbox node')

    declare_map_file_name_cmd = DeclareLaunchArgument(
        'map_file_name',
        default_value=os.path.join(get_package_share_directory("leo_nav"),
                                   'maps', 'default_map.yaml'),
        description='Full path to the map file to use for the slam_toolbox node')

    start_localization_slam_toolbox_node = LifecycleNode(
        parameters=[
          slam_params_file,
          {
            'map_file_name': map_file_name,
          }
    ],
    package='slam_toolbox',
        executable='localization_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        namespace=''
    )

    configure_event = EmitEvent(
        event=ChangeState(
            lifecycle_node_matcher=matches_action(start_localization_slam_toolbox_node),
            transition_id=Transition.TRANSITION_CONFIGURE
        )
    )

    activate_event = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=start_localization_slam_toolbox_node,
            start_state="configuring",
            goal_state="inactive",
            entities=[
                LogInfo(msg="[LifecycleLaunch] Slamtoolbox node is activating."),
                EmitEvent(event=ChangeState(
                    lifecycle_node_matcher=matches_action(start_localization_slam_toolbox_node),
                    transition_id=Transition.TRANSITION_ACTIVATE
                ))
            ]
        )
    )

    ld = LaunchDescription()

    ld.add_action(declare_slam_params_file_cmd)
    ld.add_action(declare_map_file_name_cmd)
    ld.add_action(start_localization_slam_toolbox_node)
    ld.add_action(configure_event)
    ld.add_action(activate_event)

    return ld