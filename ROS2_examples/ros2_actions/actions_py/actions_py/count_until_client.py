#!/usr/bin/env python3

from my_robot_interfaces.action import CountUntil
import rclpy
from rclpy.action import ActionClient
from rclpy.action.client import GoalStatus
from rclpy.node import Node


class CountUntilClientNode(Node):
    def __init__(self) -> None:
        super().__init__('count_until_client')
        self.count_until_client_ = ActionClient(self, CountUntil, 'count_until')
        self.goal_handle_ = None

        # --- Cancellation demo knobs (tweak these to play with cancel behavior) ---
        self.enable_cancel_ = False          # set to False to disable cancel request
        self.cancel_after_sec_ = 2.5        # seconds after goal accepted to request cancel
        # -----------------------------------------------------------------------

        self._cancel_timer = None
        self._cancel_requested = False

    def send_goal(self, target_number: int, period: float) -> None:
        # Wait for the server
        self.get_logger().info('Waiting for action server...')
        self.count_until_client_.wait_for_server()

        # Create a goal
        goal = CountUntil.Goal()
        goal.target_number = int(target_number)
        goal.period = float(period)

        # Send the goal
        self.get_logger().info(
            f'Sending goal: target_number={goal.target_number}, period={goal.period}'
        )
        self.count_until_client_.send_goal_async(
            goal, feedback_callback=self.feedback_callback
        ).add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg) -> None:
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Feedback: current_number={feedback.current_number}')

    def goal_response_callback(self, future) -> None:
        self.goal_handle_ = future.result()
        if not self.goal_handle_ or not self.goal_handle_.accepted:
            self.get_logger().warn('Goal rejected')
            if rclpy.ok():
                rclpy.shutdown()
            return

        self.get_logger().info('Goal accepted')

        # Schedule a cancel request (optional demo)
        if self.enable_cancel_ and self.cancel_after_sec_ is not None:
            # create_timer() is periodic, so cancel it after first call.
            self._cancel_timer = self.create_timer(self.cancel_after_sec_, self.cancel_goal)

        self.goal_handle_.get_result_async().add_done_callback(self.goal_result_callback)

    def cancel_goal(self) -> None:
        # timer callback, may fire multiple times if not canceled
        if self._cancel_timer is not None:
            try:
                self._cancel_timer.cancel()
            except Exception:
                pass
            self._cancel_timer = None

        if self._cancel_requested:
            return

        if self.goal_handle_ is None or not getattr(self.goal_handle_, 'accepted', False):
            self.get_logger().warn('Cancel requested before goal is accepted; ignoring')
            return

        self._cancel_requested = True
        self.get_logger().warn('Requesting goal cancel...')
        self.goal_handle_.cancel_goal_async().add_done_callback(self.cancel_done_callback)

    def cancel_done_callback(self, future) -> None:
        try:
            cancel_response = future.result()
        except Exception as exc:
            self.get_logger().error(f'Cancel service call failed: {exc!r}')
            return

        # cancel_response.goals_canceling is a list of GoalInfo that were accepted for cancel
        if getattr(cancel_response, 'goals_canceling', None):
            self.get_logger().warn('Cancel request accepted (goal is canceling)')
        else:
            self.get_logger().warn('Cancel request rejected (goal may have already finished)')

    def goal_result_callback(self, future) -> None:
        response = future.result()
        status = response.status
        result = response.result

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Final status: SUCCEEDED')
        elif status == GoalStatus.STATUS_ABORTED:
            self.get_logger().error('Final status: ABORTED')
        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().warn('Final status: CANCELED')
        else:
            self.get_logger().warn(f'Final status: UNKNOWN ({status})')

        self.get_logger().info(f'Result: reached_number={result.reached_number}')
        if rclpy.ok():
            rclpy.shutdown()


def main(args=None) -> None:
    rclpy.init(args=args)

    node = CountUntilClientNode()
    node.send_goal(6, 1.0)  # negative target_number -> server will ABORT

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
