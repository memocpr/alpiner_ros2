import rclpy
from rclpy.node import Node

class EvaluatorNode(Node):

    def __init__(self):
        super().__init__('evaluator_node')
        self.get_logger().info('Evaluator node started')

def main(args=None):
    rclpy.init(args=args)
    node = EvaluatorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()