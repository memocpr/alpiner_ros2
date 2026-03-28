import math
import csv
import os
import rclpy
from rclpy.node import Node

from nav_msgs.msg import Path, Odometry
from geometry_msgs.msg import PoseStamped


class EvaluatorNode(Node):

    def __init__(self):
        super().__init__('evaluator_node')

        self.plan = None
        self.reference_plan = None
        self.trajectory = []
        self.goal_reached_logged = False
        self.output_dir = os.path.expanduser('~/Desktop/AlpineR/alpiner_ros2/ros2_ws/src/ros2_application/evaluations')

        os.makedirs(self.output_dir, exist_ok=True)

        self.executed_path_pub = self.create_publisher(Path, '/executed_path', 10)
        self.executed_path_msg = Path()
        self.executed_path_msg.header.frame_id = 'map'

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
        if self.reference_plan is None and len(msg.poses) > 0:
            self.reference_plan = list(msg.poses)
            self.trajectory = []
            self.executed_path_msg = Path()
            self.executed_path_msg.header.frame_id = 'map'

        self.plan = msg.poses
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

        pose_stamped = PoseStamped()
        pose_stamped.header.stamp = msg.header.stamp
        pose_stamped.header.frame_id = 'map'
        pose_stamped.pose = pose
        self.executed_path_msg.header.stamp = msg.header.stamp
        self.executed_path_msg.poses.append(pose_stamped)
        self.executed_path_pub.publish(self.executed_path_msg)

        if len(self.trajectory) % 10 == 0:
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

        if dist < 0.35:
            self.get_logger().info(f'Final position error: {dist:.3f} m')
            self.save_csv()
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

    def save_csv(self):
        ref_file = os.path.join(self.output_dir, 'reference_path.csv')
        traj_file = os.path.join(self.output_dir, 'executed_path.csv')

        with open(ref_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['x', 'y'])
            for pose_stamped in self.reference_plan:
                writer.writerow([
                    pose_stamped.pose.position.x,
                    pose_stamped.pose.position.y
                ])
        self.reference_plan = None

        with open(traj_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['time', 'x', 'y', 'yaw'])
            for row in self.trajectory:
                writer.writerow(row)

        self.get_logger().info(f'CSV saved in {self.output_dir}')


def main(args=None):
    rclpy.init(args=args)
    node = EvaluatorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()