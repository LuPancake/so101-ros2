import rclpy
import math

from pathlib import Path
from rclpy.node import Node
from sensor_msgs.msg import JointState

from lerobot.robots.so_follower import SO101Follower, SO101FollowerConfig

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
        params = self.read_params()
        self.joint_publisher_ = self.create_publisher(JointState , "so101_joint_states", 10)

        self.timer_ = self.create_timer(0.5, self.publish_joint_states)
        self.use_degrees = True
        self._joint_msg = JointState()
        self._joint_msg.name = self.JOINT_NAMES
        self._positions = [0.0] * len(self.JOINT_NAMES)
        self._velocities = [0.0] * len(self.JOINT_NAMES)
        self.get_logger().info("SO101 Joint Publisher Node has been started.")

     # Initialize robot
        
        self.robot = self.create_follower(params)
        try:
            self.robot.connect(calibrate=False)
        except Exception as e :
            raise RuntimeError(f'Failed to connect to SO101 robot cause: {e}') from e

        self.last_position = None
        self.last_time = self.get_clock().now() 

    def create_follower(self,params: dict):
        config = SO101FollowerConfig(
        port=params['port'],
        # calibration_dir=Path(params['calibration_dir']),
        id=params['id'],
        use_degrees=params['use_degrees'],
        max_relative_target=params['max_relative_target'],
        disable_torque_on_disconnect=params['disable_torque_on_disconnect'],
    )
        return SO101Follower(config)

    def read_params(self) -> dict:
        self.declare_parameter('port', '/dev/ttyACM1')
        self.declare_parameter('id', 'my_so101_follower_arms')
        # self.declare_parameter('calibration_dir', str(CALIBRATION_BASE_DIR))
        self.declare_parameter('use_degrees', True)
        self.declare_parameter('max_relative_target', 0)
        self.declare_parameter('disable_torque_on_disconnect', True)
        self.declare_parameter('publish_rate', 30.0)

        max_relative_target = (
            self.get_parameter('max_relative_target').get_parameter_value().integer_value
        )
        max_relative_target = max_relative_target if max_relative_target != 0 else None

        return {
            'port': self.get_parameter('port').get_parameter_value().string_value,
            'id': self.get_parameter('id').get_parameter_value().string_value,
            # 'calibration_dir': Path(
            #     self.get_parameter('calibration_dir').get_parameter_value().string_value
            # ),
            'use_degrees': self.get_parameter('use_degrees').get_parameter_value().bool_value,
            'max_relative_target': max_relative_target,
            'disable_torque_on_disconnect': (
                self.get_parameter('disable_torque_on_disconnect').get_parameter_value().bool_value
            ),
            'publish_rate': self.get_parameter('publish_rate').get_parameter_value().double_value,
        }

    
    def get_joints_states(self):
        return self.robot.get_observation()
        
    def publish_joint_states(self):
        try:
            obs = self.get_joints_states()
            for i,joint in enumerate(self.JOINT_NAMES):
                if joint == 'gripper':
                    pos = ((obs.get(f'{joint}.pos',0.0)) / 100.0) * math.pi
                else:
                    if self.use_degrees:
                        pos = math.radians(obs.get(f'{joint}.pos',0.0))
                    else:
                        pos = ((obs.get(f'{joint}.pos',0.0)) / 100.0) * math.pi
                self._positions[i] = pos     

            self._joint_msg.header.stamp = self.get_clock().now().to_msg()
            self._joint_msg.position = self._positions
            #self._joint_msg.velocity = self._velocities
            self.joint_publisher_.publish(self._joint_msg)
        except Exception as e :
                    raise RuntimeError(f'Failed to publish joint states of SO101 robot cause:{e}')from e  


        


        
