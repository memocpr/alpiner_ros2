from loguru import logger

import numpy as np

class SteeringController:

    MAX_STEERING_CMD = 1.0                          # max steering command, in [-1.0, 1.0]
    MIN_STEERING_CMD = -1.0                         # max steering command, in [-1.0, 1.0]
    MAX_STEERING_ANGLE = 35.0                       # physical max angle of the vehicle, in degrees
    MIN_STEERING_ANGLE = -35.0                      # physical min angle of the vehicle, in degrees
    WHEEL_BASE_SQUARED = np.power(3.03, 2)          # wheel base squared, in meters, used to compute target steering angle

    def __init__(self) -> None:

        # gains
        self.p_gain = 0.0
        self.d_gain = 0.0
        self.i_gain = 0.0

        # memorized steering command, needed to avoid aggressive bumps
        self.mem_steering_cmd = 0.0
        
        # LPF filter for target steering angle
        self.lpf_target_steering_angle = OnePoleLPF(time_constant_s=0.12)

    def set_up(self, p_gain, i_gain, d_gain):
        """set up the SteeringController

        Args:
            p_gain (float): proportional gain
            i_gain (float): integral gain
            d_gain (float): derivative gain
        """
        self.p_gain = p_gain
        self.i_gain = i_gain
        self.d_gain = d_gain

        # current restriction
        if self.i_gain != 0.0:
            logger.warning("SteeringController: i_gain is not used in current implementation, set to 0.0")
            self.i_gain = 0.0
        if self.d_gain != 0.0:
            logger.warning("SteeringController: d_gain is not used in current implementation, set to 0.0")
            self.d_gain = 0.0
    
    def get_filtered_target_steering_angle(self, new_target_steering_angle, dt):
        """return the filtered target steering angle using a LPF filter

        Args:
            new_target_steering_angle (float): new target steering angle to filter
            dt (float): time difference between two calls

        Returns:
            float: filtered target steering angle
        """
        return self.lpf_target_steering_angle.update(new_target_steering_angle, dt)

    def limit_steering_changes(self, desired_command: float, dt_s: float, max_slew_rate_per_s: float = 3.0) -> float:
        """
        Apply a dt-aware slew-rate limit to keep the command continuous.

        Args:
            desired_command: Target command in [self.MIN_STEERING_CMD, self.MAX_STEERING_CMD] from the controller.
            dt_s: Elapsed time since the last update (seconds).
            max_slew_rate_per_s: Max allowed change per second (command units / s).

        Returns:
            The new, slew-limited command in [self.MIN_STEERING_CMD, self.MAX_STEERING_CMD].
        """

        desired_command = float(np.clip(desired_command, self.MIN_STEERING_CMD, self.MAX_STEERING_CMD))
        if dt_s <= 0.0:
            return desired_command

        max_step = max_slew_rate_per_s * dt_s
        requested_step = desired_command - self.mem_steering_cmd

        if requested_step > max_step:
            requested_step = max_step
        elif requested_step < -max_step:
            requested_step = -max_step

        new_command = self.mem_steering_cmd + requested_step
        self.mem_steering_cmd = new_command
        return float(np.clip(new_command, self.MIN_STEERING_CMD, self.MAX_STEERING_CMD))

    def compute_target_steering_angle(self, cmd_vel):
        """compute the target steering angle depending on the curvature

        Args:
            cmd_vel (Twist): message with curvature data

        Returns:
            float: target steering angle
        """
        # curvarture might tend toward 0.0 -> make sure we dont divide by 0.0
        radius_lookahead_arc = 1000.0
        if cmd_vel.angular.y != 0.0:
            radius_lookahead_arc = 1.0 / cmd_vel.angular.y
        logger.debug('ang.Z : {}, radius lookahead arc: {}'.format(cmd_vel.angular.z, radius_lookahead_arc))
        
        # compute targeted steering angle, given radius of the lookahead_arc and wheelbase length
        # check atcom-docs for info on the formula
        radius_lookahead_arc_squared_time_4 = 4* np.power(radius_lookahead_arc, 2)
        target_steering_angle = np.arccos((radius_lookahead_arc_squared_time_4 - SteeringController.WHEEL_BASE_SQUARED) / (radius_lookahead_arc_squared_time_4 + SteeringController.WHEEL_BASE_SQUARED))
        target_steering_angle = np.rad2deg(target_steering_angle)
        target_steering_angle = abs(target_steering_angle) # sign is computed later
        return target_steering_angle

    def compute_sign_target_steering_angle(self, cmd_vel, lin_speed_machine):
        """
        angular velocity Z is + when:
            * going FW and steering to the left
            * going BW and steering to the right
        angular velocity Z is - when :
            * going FW and steering to the right
            * going BW and steering to the left

        steering to the left means : steering angle is negative, and so is the steering command
            * positive angular velocity Z and going FW
            * negative angular velocity Z and going BW
        steering to the right means : steering angle is positive, and so is the steering command
            * positive angular velocity Z and going BW
            * negative angular velocity Z and going FW
        """

        # going FW
        if lin_speed_machine >= 0.0:
            if cmd_vel.angular.z >= 0.0:
                return -1.0
            else:
                return 1.0
        # going BW
        else:
            if cmd_vel.angular.z >= 0.0:
                return 1.0
            else:
                return -1.0 

    def compute_steering_on_angle(self, mem_machine_ind_all, dt, target_steering_angle):
        """compute steering command based on the targeted steering angle (deg)."""

        # compute error
        target_deg   = float(np.clip(target_steering_angle, self.MIN_STEERING_ANGLE, self.MAX_STEERING_ANGLE))
        measured_deg = float(mem_machine_ind_all.steering_angle)  # assumed already filtered upstream
        angle_error_deg = target_deg - measured_deg
        logger.debug('target_deg: {}, measured_deg: {}'.format(target_deg, measured_deg))

        # Proportional contribution
        p_contrib = self.p_gain * angle_error_deg

        # Desired command before slew, clipped to actuator limits
        cmd_desired = p_contrib
        cmd_desired = float(np.clip(cmd_desired, self.MIN_STEERING_CMD, self.MAX_STEERING_CMD))

        # dt-aware slew limiting for cabin comfort (tune rate if needed)
        cmd_slewed = self.limit_steering_changes(cmd_desired, dt, max_slew_rate_per_s=3.0)
        return cmd_slewed
    

class OnePoleLPF:
    """
    First-order low-pass filter with a fixed time constant (seconds).
    dt-aware update: alpha = clamp(dt_s / time_constant_s, 0, 1).
    """
    def __init__(self, time_constant_s: float, initial_output: float | None = None):
        """Initialize the filter.
        Args:
            time_constant_s: Time constant in seconds, must be > 0.0.
            initial_output: Initial output value, or None to initialize at first input.
        """
        self.time_constant_s = max(float(time_constant_s), 1e-3)
        self.filtered_value = float(initial_output) if initial_output is not None else None

    def reset(self, value: float) -> None:
        """Reset the filter to a specific value.
        Args:
            value: Value to set the filter output to.
        """
        self.filtered_value = float(value)

    def update(self, input_value: float, dt_s: float) -> float:
        """Update the filter with a new input value and elapsed time.
        Args:
            input_value: New input value to filter.
            dt_s: Elapsed time since the last update (seconds).
        Returns:
            The new filtered output value.
        """
        if self.filtered_value is None:
            self.filtered_value = float(input_value)
            return self.filtered_value

        # dt-aware smoothing factor in [0, 1]
        alpha = dt_s / self.time_constant_s
        if alpha < 0.0:
            alpha = 0.0
        elif alpha > 1.0:
            alpha = 1.0

        self.filtered_value += alpha * (float(input_value) - self.filtered_value)
        return self.filtered_value
