import math
import rclpy
from rclpy.node import Node

from nav_msgs.msg import Path, Odometry


class EvaluatorNode(Node):

    def __init__(self):
        super().__init__('evaluator_node')

        self.plan = None
        self.trajectory = []
        self.goal_reached_logged = False

        self.create_subscription(
            Path,
            '/plan',
            self.plan_callback,
            10
        )

        self.create_subscription(
            Odometry,
            '/odometry/filtered_local',
            self.odom_callback,
            10
        )

        self.get_logger().info('Evaluator node started')

    def plan_callback(self, msg):
        self.plan = msg.poses
        self.trajectory = []
        self.goal_reached_logged = False

    def odom_callback(self, msg):
        if self.goal_reached_logged:
            return

        pose = msg.pose.pose

        x = pose.position.x
        y = pose.position.y

        q = pose.orientation
        yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        )

        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

        self.trajectory.append((t, x, y, yaw))

        if len(self.trajectory) % 40 == 0:
            self.compute_cross_track_error()
            self.compute_final_error()

    def compute_final_error(self):
        if not self.plan or not self.trajectory:
            return

        goal = self.plan[-1].pose.position
        last = self.trajectory[-1]

        dx = last[1] - goal.x
        dy = last[2] - goal.y
        dist = (dx**2 + dy**2)**0.5

        if dist < 1.5:
            self.get_logger().info(f'Final position error: {dist:.3f} m')
            self.goal_reached_logged = True

    def compute_cross_track_error(self):
        if not self.plan or not self.trajectory:
            return

        last = self.trajectory[-1]
        rx = last[1]
        ry = last[2]

        min_dist = float('inf')

        for pose_stamped in self.plan:
            px = pose_stamped.pose.position.x
            py = pose_stamped.pose.position.y
            dist = ((rx - px)**2 + (ry - py)**2)**0.5
            if dist < min_dist:
                min_dist = dist

        self.get_logger().info(f'Cross-track error: {min_dist:.3f} m')


def main(args=None):
    rclpy.init(args=args)
    node = EvaluatorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()