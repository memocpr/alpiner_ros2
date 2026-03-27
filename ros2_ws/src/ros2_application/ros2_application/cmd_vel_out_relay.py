import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class CmdVelRelay(Node):
    def __init__(self):
        super().__init__('cmd_vel_to_cmd_vel_out_relay')
        self.pub = self.create_publisher(Twist, '/cmd_vel_out', 10)
        self.sub = self.create_subscription(Twist, '/cmd_vel', self._cb, 10)

    def _cb(self, msg: Twist):
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelRelay()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()