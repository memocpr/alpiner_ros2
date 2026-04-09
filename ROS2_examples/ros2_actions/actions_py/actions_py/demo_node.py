import rclpy
from rclpy.node import Node


class DemoNode(Node):
    def __init__(self) -> None:
        super().__init__('actions_py_demo')
        self.get_logger().info('actions_py demo node is running')
        self._timer = self.create_timer(1.0, self._on_timer)
        self._count = 0

    def _on_timer(self) -> None:
        self._count += 1
        self.get_logger().info(f'tick: {self._count}')


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DemoNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
