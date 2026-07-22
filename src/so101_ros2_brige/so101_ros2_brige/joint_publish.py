import rclpy
import numpy
import math

from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray

from lerobot.robots.so_follower import SO101Follower

class SO101JointPublish (Node):
    JOINT_NAMES = [
        'shoulder_pan',
        'shoulder_lift',
        'elbow_flex',
        'wrist_flex',
        'wrist_roll',
        'gripper',
    ]

    def __init__(self):
        super().__init__("so101_joint_publish")
        self.joint_publisher_ = self.create_publisher(JointState , "joint_states", 10)

        self.timer_ = self.create_timer(1.0, self.publish_joint_states)

        self.robot = SO101Follower()

        self.joint_msg = JointState()
        self.joint_msg.name = self.JOINT_NAMES
        self._positions = [0.0] * len(self.JOINT_NAMES)
        self._velocities = [0.0] * len(self.JOINT_NAMES)
        self.get_logger().info("SO101 Joint Publisher Node has been started.")

    def publish_joint_states(self):
        self.joint_msg.header.stamp = self.get_clock().now().to_msg()
        self.joint_msg.header.frame_id = ""
        


        
