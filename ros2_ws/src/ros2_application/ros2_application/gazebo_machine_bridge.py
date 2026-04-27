#!/usr/bin/env python3

import math
from typing import Optional

import rclpy
from rclpy.executors import ExternalShutdownException
from gazebo_msgs.srv import SetModelConfiguration
from nav_msgs.msg import Odometry
from rclpy.node import Node
from geometry_msgs.msg import Twist
from ros2_interfaces.msg import MachineIndAll, MachineSetAll


class GazeboMachineBridge(Node):
    """Bridge simulated machine commands to Gazebo and feed back MachineIndAll."""

    DM_FORWARD = 8
    DM_REVERSE = 9
    DM_NEUTRAL = 10

    SPEED_SIGN_FORWARD = 11
    SPEED_SIGN_REVERSE = 12

    def __init__(self) -> None:
        super().__init__('gazebo_machine_bridge')

        self.declare_parameter('machine_cmd_topic', '/atcom_wa380/wheeler/write/nav_ctrl')
        self.declare_parameter('machine_feedback_topic', '/atcom_wa380/wheeler/read/all')
        self.declare_parameter('odom_topic', '/odom')
        self.declare_parameter('cmd_vel_out_topic', '/cmd_vel_ll')
        self.declare_parameter('model_name', 'komatsu')
        self.declare_parameter('urdf_param_name', 'robot_description')
        self.declare_parameter('articulation_joint_name', 'articulation_to_front')
        self.declare_parameter('wheelbase_m', 3.03)
        self.declare_parameter('max_forward_speed_mps', 2.2)
        self.declare_parameter('max_reverse_speed_mps', 1.4)
        self.declare_parameter('max_brake_decel_mps2', 2.0)
        self.declare_parameter('throttle_accel_mps2', 1.2)
        self.declare_parameter('max_articulation_angle_deg', 35.0)
        self.declare_parameter('max_articulation_rate_degps', 45.0)

        self.machine_cmd_topic = self.get_parameter('machine_cmd_topic').value
        self.machine_feedback_topic = self.get_parameter('machine_feedback_topic').value
        self.odom_topic = self.get_parameter('odom_topic').value
        self.cmd_vel_out_topic = self.get_parameter('cmd_vel_out_topic').value
        self.model_name = self.get_parameter('model_name').value
        self.urdf_param_name = self.get_parameter('urdf_param_name').value
        self.articulation_joint_name = self.get_parameter('articulation_joint_name').value

        self.wheelbase_m = float(self.get_parameter('wheelbase_m').value)
        self.max_forward_speed_mps = float(self.get_parameter('max_forward_speed_mps').value)
        self.max_reverse_speed_mps = float(self.get_parameter('max_reverse_speed_mps').value)
        self.max_brake_decel_mps2 = float(self.get_parameter('max_brake_decel_mps2').value)
        self.throttle_accel_mps2 = float(self.get_parameter('throttle_accel_mps2').value)
        self.max_articulation_angle_rad = math.radians(
            float(self.get_parameter('max_articulation_angle_deg').value)
        )
        self.max_articulation_rate_radps = math.radians(
            float(self.get_parameter('max_articulation_rate_degps').value)
        )

        self.latest_cmd: Optional[MachineSetAll] = None
        self.last_odom: Optional[Odometry] = None
        self.current_speed_cmd = 0.0
        self.current_articulation_rad = 0.0
        self.last_update_time = self.get_clock().now()
        self._set_joint_future = None

        self.create_subscription(MachineSetAll, self.machine_cmd_topic, self._on_machine_cmd, 20)
        self.create_subscription(Odometry, self.odom_topic, self._on_odom, 20)

        self.cmd_vel_pub = self.create_publisher(Twist, self.cmd_vel_out_topic, 20)
        self.machine_ind_pub = self.create_publisher(MachineIndAll, self.machine_feedback_topic, 20)

        self.set_joint_client = self.create_client(SetModelConfiguration, '/gazebo/set_model_configuration')
        self.create_timer(0.05, self._on_timer)

    def _on_machine_cmd(self, msg: MachineSetAll) -> None:
        self.latest_cmd = msg

    def _on_odom(self, msg: Odometry) -> None:
        self.last_odom = msg

    @staticmethod
    def _clamp(value: float, low: float, high: float) -> float:
        return max(low, min(high, value))

    def _step_towards(self, current: float, target: float, max_step: float) -> float:
        delta = target - current
        if delta > max_step:
            return current + max_step
        if delta < -max_step:
            return current - max_step
        return target

    def _target_speed(self, cmd: MachineSetAll) -> float:
        parking_brake_active = cmd.options.parking_brake > 0
        if parking_brake_active:
            return 0.0

        throttle = self._clamp(float(cmd.throttle), 0.0, 1.0)
        if cmd.directional_sel == self.DM_FORWARD:
            return throttle * self.max_forward_speed_mps
        if cmd.directional_sel == self.DM_REVERSE:
            return -throttle * self.max_reverse_speed_mps
        return 0.0

    def _target_articulation(self, cmd: MachineSetAll) -> float:
        steering = self._clamp(float(cmd.steering), -1.0, 1.0)
        return steering * self.max_articulation_angle_rad

    def _publish_machine_feedback(self) -> None:
        msg = MachineIndAll()

        odom_speed = 0.0
        odom_yaw_rate = 0.0
        if self.last_odom is not None:
            odom_speed = float(self.last_odom.twist.twist.linear.x)
            odom_yaw_rate = float(self.last_odom.twist.twist.angular.z)

        msg.speed = odom_speed
        msg.speed_sign = self.SPEED_SIGN_FORWARD if odom_speed >= 0.0 else self.SPEED_SIGN_REVERSE
        msg.flag_speed_signing_uncertain = False
        msg.angular_velocity = odom_yaw_rate
        msg.directional_mode = self.DM_NEUTRAL if abs(self.current_speed_cmd) < 0.03 else (
            self.DM_FORWARD if self.current_speed_cmd > 0.0 else self.DM_REVERSE
        )
        msg.gear_speed = 1
        msg.bellcrank_angle = 0.0
        msg.steering_angle = math.degrees(self.current_articulation_rad)
        msg.heartbeat_sps = 0
        msg.throttle_pedal = self._clamp(abs(self.current_speed_cmd) / self.max_forward_speed_mps, 0.0, 1.0)
        msg.brake_pressure = 0.0
        msg.registers = [0] * 10
        msg.tm_pmi = 0.0
        msg.tm_ros = self.get_clock().now().nanoseconds / 1e9

        msg.others.op_mode_hw = 3
        msg.others.engine_is_on = True
        msg.others.parking_brake_is_on = False
        msg.others.ppc_is_locked = False
        msg.others.speed_limitation = False

        msg.errors.es_btn = False
        msg.errors.zone_safe = False
        msg.errors.os3_error_rear = False
        msg.errors.os3_error_front = False
        msg.errors.os3_warn_rear = False
        msg.errors.os3_warn_front = False
        msg.errors.os3_protect_rear = False
        msg.errors.os3_protect_front = False
        msg.errors.baumer = False
        msg.errors.es_btn_2 = False
        msg.errors.shovel_position = False
        msg.errors.heartbeat = False

        self.machine_ind_pub.publish(msg)

    def _publish_cmd_vel(self) -> None:
        twist = Twist()
        twist.linear.x = self.current_speed_cmd
        if abs(self.wheelbase_m) > 1e-6:
            twist.angular.z = self.current_speed_cmd * math.tan(self.current_articulation_rad) / self.wheelbase_m
        self.cmd_vel_pub.publish(twist)

    def _update_articulation_in_gazebo(self) -> None:
        if not self.set_joint_client.service_is_ready():
            return
        if self._set_joint_future is not None and not self._set_joint_future.done():
            return

        req = SetModelConfiguration.Request()
        req.model_name = self.model_name
        req.urdf_param_name = self.urdf_param_name
        req.joint_names = [self.articulation_joint_name]
        req.joint_positions = [self.current_articulation_rad]
        self._set_joint_future = self.set_joint_client.call_async(req)

    def _on_timer(self) -> None:
        now = self.get_clock().now()
        dt = (now - self.last_update_time).nanoseconds * 1e-9
        self.last_update_time = now
        if dt <= 0.0:
            return

        cmd = self.latest_cmd
        if cmd is None:
            self.current_speed_cmd = self._step_towards(
                self.current_speed_cmd,
                0.0,
                self.max_brake_decel_mps2 * dt,
            )
            self.current_articulation_rad = self._step_towards(
                self.current_articulation_rad,
                0.0,
                self.max_articulation_rate_radps * dt,
            )
        else:
            speed_target = self._target_speed(cmd)
            articulation_target = self._target_articulation(cmd)

            brake = self._clamp(float(cmd.brake), 0.0, 1.0)
            speed_step = self.throttle_accel_mps2 * dt
            if brake > 1e-3:
                speed_step = (self.max_brake_decel_mps2 * max(brake, 0.2)) * dt

            self.current_speed_cmd = self._step_towards(self.current_speed_cmd, speed_target, speed_step)
            self.current_articulation_rad = self._step_towards(
                self.current_articulation_rad,
                articulation_target,
                self.max_articulation_rate_radps * dt,
            )

        self._publish_cmd_vel()
        self._update_articulation_in_gazebo()
        self._publish_machine_feedback()


def main() -> None:
    rclpy.init()
    node = GazeboMachineBridge()
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

