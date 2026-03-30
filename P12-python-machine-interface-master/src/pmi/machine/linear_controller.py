from loguru import logger
import time

class LinearController:

    # speed limits
    MAX_SPEED_NORMAL_MODE = 5.555 # m/s -> 20 km/h, this constant is always positive, but real speed can be negative as well
    MAX_SPEED_WARNING_MODE = 1.388 # m/s -> 5 km/h, this constant is always positive, but real speed can be negative as well

    # throttle and brake commands
    MAX_THROTTLE = 1.0 # full range
    MAX_BRAKE = 1.0    # full range
    MAX_USABLE_BRAKE = 0.6 # only when we need to restrict speed due to throttle limiter being on, otherwise we use values up to 1.0 from the controller when the driver is actively braking
    DEFAULT_BRAKE = 0.4 # a value that is efficient yet not to harsh
    MAX_STEERING = 1.0 # full range
    MIN_STEERING = -1.0 # full range
    
    def __init__(self) -> None:
        # gains to be set up later
        self._p_gain_throttle = 0.0
        self._p_gain_brake = 0.0

    def set_up(self, p_gain_throttle: float, p_gain_brake: float) -> None:
        """
        Set up the linear controller with proportional gains for throttle and brake.
        :param p_gain_throttle: Proportional gain for throttle control
        :param p_gain_brake: Proportional gain for brake control
        """
        self._p_gain_throttle = p_gain_throttle
        self._p_gain_brake = p_gain_brake
        logger.info(f"LinearController set up with p_gain_throttle: {p_gain_throttle}, p_gain_brake: {p_gain_brake}")

    def compute_remote_control(self, machine_ind_all, required_throttle : float, required_brake : float, required_steering : float) -> tuple[float, float, float]:
        """
        Compute the final throttle, brake, and steering commands based on required inputs and machine state.
        This method might reduces throttle, and increase brakes, depending on the speed limitation status.
        :param machine_ind_all: MachineIndAll object containing the current state of the machine
        :param required_throttle: Required throttle command from the user
        :param required_brake: Required brake command from the user
        :param required_steering: Required steering command from the user
        :return: Tuple of (throttle_out, brake_out, steering_out) commands"""
        # output variables
        throttle_out = max(min(required_throttle, LinearController.MAX_THROTTLE), 0.0)
        brake_out = max(min(required_brake, LinearController.MAX_BRAKE), 0.0)
        steering_out = max(min(required_steering, LinearController.MAX_STEERING), LinearController.MIN_STEERING) 

        # input variables
        if machine_ind_all is None:
            logger.error('machine_ind_all is None -> returning required commands without any limiting')
            return throttle_out, brake_out, steering_out
        speed = machine_ind_all.speed # m/s, positive forward, negative backward

        # limit throttle and brake
        throttle_out, brake_out = self.limiter(throttle_out, brake_out, machine_ind_all)

        # make sure new brake_out is not smaller than required_brake
        # we want to limitate speed if required, but not completely override driver commands
        if brake_out < required_brake:
            brake_out = max(min(required_brake, LinearController.MAX_BRAKE), 0.0)
            logger.debug('Adjusted brake_out to be at least required_brake: {:.3f}'.format(required_brake))

        # make sure new throttle_out is not bigger than required_throttle
        if throttle_out > required_throttle:
            throttle_out = max(min(required_throttle, LinearController.MAX_THROTTLE), 0.0)
            logger.debug('Adjusted throttle_out to be at most required_throttle: {:.3f}'.format(required_throttle))

        # limit steering, depending on the speed
        # this reduces the risk of going off-track at high speed
        steering_out = LinearController._limit_steering_on_speed(speed, required_steering)

        return throttle_out, brake_out, steering_out
    
    def compute_nav_control(self, speed, target_speed, dt):
        """
        Compute throttle and brake commands based on current speed, target speed, and time delta.
        :param speed: Current speed of the vehicle (m/s)
        :param target_speed: Desired target speed (m/s)
        :param dt: Time elapsed since last update (s)
        :return: Tuple of (throttle, brake) commands
        """
        logger.warning('compute_nav_control not implemented yet')
        pass

    def limiter(self, throttle : float, brake : float, machine_ind_all) -> tuple[float, float]:
        """
        Check if the required throttle and brake commands match speed limits.
        :param throttle: User required throttle command
        :param brake: User required brake command
        :param machine_ind_all: MachineIndAll object
        :return: Tuple of (throttle, brake) commands adjusted for warning mode if necessary
        """
        
        # output variables
        throttle_out = throttle
        brake_out = brake

        # input variables
        speed : float = machine_ind_all.speed # m/s, positive forward, negative backward
        speed_limitation : bool = machine_ind_all.others.speed_limitation

        # which limits will we use ? depends on feedback from machine's safety sensors
        max_speed_limit_abs : float = LinearController.MAX_SPEED_WARNING_MODE
        if not speed_limitation:
            max_speed_limit_abs = LinearController.MAX_SPEED_NORMAL_MODE

        # early speed limit to avoid overshooting
        EARLY_SPEED_LIMIT_OFFSET = 0.35 # m/s -> 1.26 km/h
        early_max_speed_limit_abs = max(0.0, (max_speed_limit_abs - EARLY_SPEED_LIMIT_OFFSET))
        
        # what is the situation with the vehicle ?
        is_vehicle_moving : bool = abs(speed) > 0.1 # true if vehicle is moving, either forward or backward
            
        # vehicle is nearly stopped, no need to limit anything
        if is_vehicle_moving == False:
            return throttle_out, brake_out

        # speed is within early limits, both negative and positive
        # no change
        elif abs(speed) <= early_max_speed_limit_abs:
            return throttle_out, brake_out

        # speed is too high -> limiting 
        else: 

            # how much faster are we : compared to the early limit 
            # speed is for sure bigger than early limit here
            delta_speed_abs = abs(speed) - early_max_speed_limit_abs # m/s, always positive

            # small exceedance -> reduce throttle
            # max 0.25 m/s = 0.9 km/h tolerance and not increasing abs speed
            if (delta_speed_abs < (0.25 + EARLY_SPEED_LIMIT_OFFSET)):
                logger.debug('A bit too fast {:.3f} m/s instead of {:.3f} -> red. throttle, same brake'.format(delta_speed_abs, max_speed_limit_abs))
                
                # adjust throttle
                throttle_out = throttle_out * LinearController._limit_throttle_on_delta_speed(delta_speed_abs)
                return throttle_out, brake_out

            # anything else, we need to take actions
            else:
                logger.debug('Significantly too fast {:.3f} m/s instead of {:.3f} -> adjust throttle/brake'.format(delta_speed_abs, max_speed_limit_abs))
                throttle_out = 0.0 # cut throttle completely
 
                # brake is proportional to how much we exceed the speed limit
                brake_out = self._p_gain_brake * (delta_speed_abs ** 2) # quadratic relation

                # limit to MAX_USABLE_BRAKE in this case, but if operator requests more, more will be applied
                brake_out = min(brake_out, LinearController.MAX_USABLE_BRAKE)
                brake_out = max(brake_out, 0.0) # limit to minimum 0.0
                return throttle_out, brake_out
    
    def _limit_throttle_on_delta_speed(delta_speed : float) -> float:
        """
        Limit throttle based on how much the speed exceeds the maximum allowed speed.
        :param delta_speed: Amount by which the current speed exceeds the maximum allowed speed (m/s)
        :return: Limited throttle command in the range [0.0, 1.0]
        """
        # reduce throttle more and more as delta_speed increases
        # if delta_speed ~= 0.0 -> coeff_throttle = 1.0
        # if delta_speed ~= 0.25 -> coeff_throttle = 0.25
        # if delta_speed >= 0.5 -> coeff_throttle = 0.14
        coeff_throttle = 1.0 / (1.0 + delta_speed * 16)
        coeff_throttle = max(coeff_throttle, 0.0) # ensure non-negative
        coeff_throttle = min(coeff_throttle, 1.0) # ensure not above 1.0
        return coeff_throttle
    
    def _limit_steering_on_speed(speed : float, required_steering : float) -> float:
        """
        Limit steering based on current speed.
        :param speed: Current speed of the vehicle (m/s)
        :param required_steering: Required steering command
        :return: Limited steering command
        """
        if abs(speed) < 1.5: # 1.5 m/s -> no reduction
            return required_steering
        elif abs(speed) < 3.0: # 3 m/s -> 0.75 reduction
            logger.debug('Steering reduced to 75% due to speed {:.3f} m/s'.format(speed))
            return 0.75 * required_steering
        else: # above 3 m/s -> 0.5 reduction
            logger.debug('Steering reduced to 50% due to speed {:.3f} m/s'.format(speed))
            return 0.5 * required_steering

