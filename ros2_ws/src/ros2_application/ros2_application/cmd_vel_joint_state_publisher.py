import math
from typing import Dict

import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import JointState


class CmdVelJointStatePublisher(Node):
    def __init__(self):
        super().__init__('cmd_vel_joint_state_publisher')

        self.declare_parameter('cmd_vel_topic', '/cmd_vel')
        self.declare_parameter('joint_state_topic', '/joint_states')
        self.declare_parameter('publish_rate_hz', 30.0)
        self.declare_parameter('wheel_radius', 0.8)
        self.declare_parameter('track_width', 2.16)
        self.declare_parameter('wheel_base', 3.03)
        self.declare_parameter('max_articulation_angle', 0.35)
        self.declare_parameter('cmd_timeout_sec', 0.5)

        self.cmd_vel_topic = str(self.get_parameter('cmd_vel_topic').value)
        self.joint_state_topic = str(self.get_parameter('joint_state_topic').value)
        self.publish_rate_hz = float(self.get_parameter('publish_rate_hz').value)
        self.wheel_radius = float(self.get_parameter('wheel_radius').value)
        self.track_width = float(self.get_parameter('track_width').value)
        self.wheel_base = float(self.get_parameter('wheel_base').value)
        self.max_articulation_angle = float(self.get_parameter('max_articulation_angle').value)
        self.cmd_timeout_sec = float(self.get_parameter('cmd_timeout_sec').value)

        self.joint_names = [
            'articulation_to_front',
            'front_left_wheel_joint',
            'front_right_wheel_joint',
            'rear_left_wheel_joint',
            'rear_right_wheel_joint',
        ]
        self.joint_positions: Dict[str, float] = {name: 0.0 for name in self.joint_names}

        self.last_cmd = Twist()
        self.last_cmd_stamp = self.get_clock().now()
        self.last_update_stamp = self.get_clock().now()

        self.subscription = self.create_subscription(
            Twist,
            self.cmd_vel_topic,
            self._on_cmd_vel,
            10,
        )
        self.publisher = self.create_publisher(JointState, self.joint_state_topic, 10)
        self.timer = self.create_timer(1.0 / max(self.publish_rate_hz, 1.0), self._on_timer)

        self.get_logger().info(
            f'Publishing simulated joint states from {self.cmd_vel_topic} to {self.joint_state_topic}'
        )

    def _on_cmd_vel(self, msg: Twist):
        self.last_cmd = msg
        self.last_cmd_stamp = self.get_clock().now()

    def _compute_articulation_angle(self, linear_x: float, angular_z: float) -> float:
        if abs(linear_x) < 1e-3:
            return 0.0

        curvature = angular_z / linear_x
        argument = max(-1.0, min(1.0, 0.5 * self.wheel_base * curvature))
        articulation_angle = 2.0 * math.asin(argument)
        return max(-self.max_articulation_angle, min(self.max_articulation_angle, articulation_angle))

    def _on_timer(self):
        now = self.get_clock().now()
        dt = (now - self.last_update_stamp).nanoseconds * 1e-9
        self.last_update_stamp = now
        if dt <= 0.0:
            return

        cmd_age = (now - self.last_cmd_stamp).nanoseconds * 1e-9
        if cmd_age > self.cmd_timeout_sec:
            linear_x = 0.0
            angular_z = 0.0
        else:
            linear_x = float(self.last_cmd.linear.x)
            angular_z = float(self.last_cmd.angular.z)

        articulation_angle = self._compute_articulation_angle(linear_x, angular_z)

        left_velocity = linear_x - 0.5 * self.track_width * angular_z
        right_velocity = linear_x + 0.5 * self.track_width * angular_z

        if self.wheel_radius <= 1e-6:
            wheel_left_rad_s = 0.0
            wheel_right_rad_s = 0.0
        else:
            wheel_left_rad_s = left_velocity / self.wheel_radius
            wheel_right_rad_s = right_velocity / self.wheel_radius

        self.joint_positions['articulation_to_front'] = articulation_angle
        self.joint_positions['front_left_wheel_joint'] += wheel_left_rad_s * dt
        self.joint_positions['rear_left_wheel_joint'] += wheel_left_rad_s * dt
        self.joint_positions['front_right_wheel_joint'] += wheel_right_rad_s * dt
        self.joint_positions['rear_right_wheel_joint'] += wheel_right_rad_s * dt

        msg = JointState()
        msg.header.stamp = now.to_msg()
        msg.name = self.joint_names
        msg.position = [self.joint_positions[name] for name in self.joint_names]
        msg.velocity = [
            0.0,
            wheel_left_rad_s,
            wheel_right_rad_s,
            wheel_left_rad_s,
            wheel_right_rad_s,
        ]
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelJointStatePublisher()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
