#!/usr/bin/env python3

import time

from my_robot_interfaces.action import CountUntil
import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node


class CountUntilServerNode(Node):
    def __init__(self) -> None:
        super().__init__('count_until_server')

        # Allow action callbacks (goal/cancel/execute) to be re-entrant when using a multi-threaded executor.
        self._cb_group = ReentrantCallbackGroup()

        self._server = ActionServer(
            self,
            CountUntil,
            'count_until',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self._cb_group,
        )

        self.get_logger().info('Action server has been started')

    def destroy_node(self):
        # Make sure the server is cleaned up before shutting down the node.
        self._server.destroy()
        super().destroy_node()

    def goal_callback(self, goal_request: CountUntil.Goal) -> GoalResponse:
        # NOTE: We accept negative target_number too, and handle it during execution by aborting.
        # This allows clients to receive an ABORTED status instead of a REJECTED goal.
        if goal_request.period <= 0.0:
            self.get_logger().warn('Rejected goal: period must be > 0.0')
            return GoalResponse.REJECT

        self.get_logger().info(
            f'Accepted goal: target={goal_request.target_number}, period={goal_request.period}'
        )
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle) -> CancelResponse:
        self.get_logger().info('Received request to cancel goal')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        # Get request from goal
        target_number = goal_handle.request.target_number
        period = goal_handle.request.period

        # Execute the action
        self.get_logger().info('Executing the goal')

        # Abort logic: negative target_number is considered an execution-time failure.
        if target_number < 0:
            self.get_logger().error('Aborting goal: target_number must be >= 0')
            result = CountUntil.Result()
            result.reached_number = 0
            goal_handle.abort()
            # rclpy uses exceptions to indicate terminal states when leaving execute_callback.
            raise ActionServer.AbortException(result)

        counter = 0
        feedback = CountUntil.Feedback()

        for _ in range(int(target_number)):
            if goal_handle.is_cancel_requested:
                result = CountUntil.Result()
                result.reached_number = counter
                goal_handle.canceled()
                self.get_logger().info(f'Goal canceled at {counter}')
                return result

            counter += 1
            self.get_logger().info(str(counter))

            # Optional: publish feedback (nice for clients)
            feedback.current_number = counter
            goal_handle.publish_feedback(feedback)

            time.sleep(period)

        # Once done, set goal final state
        goal_handle.succeed()

        # and send the result
        result = CountUntil.Result()
        result.reached_number = counter
        return result


def main(args=None) -> None:
    rclpy.init(args=args)

    node = CountUntilServerNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
