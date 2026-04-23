from loguru import logger

class LinearController:

    # driving constants
    MAX_THROTTLE_CMD = 0.5
    MAX_BRAKE_CMD = 0.5
    BRAKE_USUAL_VALUE = 0.3

    # constructor
    def __init__(self) -> None:
        self.throttle_reduction_factor = 0.0
        self.p_gain_linear_speed = 0.0
        self.p_gain_brake = 0.0

    # init values for controller
    def set_up(self, throttle_reduction_factor, p_gain_linear_speed, p_gain_brake):
        """set up LinearController

        Args:
            throttle_reduction_factor (float): how much do we reduce throttle when decreasing a little bit speed
            p_gain_linear_speed (float): proportional gain throttle
            p_gain_brake (float): proportional gain braking
        """
        self.throttle_reduction_factor = throttle_reduction_factor
        self.p_gain_linear_speed = p_gain_linear_speed
        self.p_gain_brake = p_gain_brake
        
    # compute throttle and brake when going forward
    def compute_throttle_brake_FW(self, delta_lin_speed, dt, target_speed):
        """compute brake and throttle for forward

        Args:
            delta_lin_speed (float): difference between targeted and actual linear speed
            dt (float): main timer clockout value
            target_speed (float): targeted linear speed value

        Returns:
            (float, float): (throttle, brake)
        """
        throttle = 0.0
        brake = 0.0
        
        # delta speed is negative, meaning that we are going to fast 
        if delta_lin_speed < 0.0:
            #logger.debug('delta speed {} is negative -> brake or reduce throttle'.format(delta_lin_speed))
            brake = self.compute_brake(delta_lin_speed, target_speed)

            # if no brake, then reduce throttle
            if brake == 0.0:
                #logger.debug('decreasing throttle command, because we dont brake')
                throttle = self.throttle_reduction_factor * self.compute_throttle(delta_lin_speed, dt)
            else:
                throttle = 0.0
            return throttle, brake
        
        # delta speed is positive, meaning that we must increase speed
        else:
            #logger.debug('delta speed {} is positive -> increase throttle'.format(delta_lin_speed))
            throttle = self.compute_throttle(delta_lin_speed, dt)
            brake = 0.0
            return throttle, brake
        
    # compute throttle and brake when going backward
    def compute_throttle_brake_BW(self, delta_lin_speed, dt, target_speed):
        """compute brake and throttle for backward

        Args:
            delta_lin_speed (float): difference between targeted and actual linear speed
            dt (float): main timer clockout value
            target_speed (float): targeted linear speed value

        Returns:
            (float, float): (throttle, brake)
        """
        throttle = 0.0
        brake = 0.0
        
        # delta speed is positive, meaning that we are going to fast 
        if delta_lin_speed > 0.0:
            #logger.debug('delta speed {} is positive -> brake or reduce throttle'.format(delta_lin_speed))
            brake = self.compute_brake(delta_lin_speed, target_speed)

            # if brake is 0.0 because we're close to targeted speed, we must only reduce throttle
            if brake == 0.0:
                #logger.debug('decreasing throttle, because we dont brake')
                throttle = self.throttle_reduction_factor * self.compute_throttle(delta_lin_speed, dt)
            else:
                throttle = 0.0
            return throttle, brake
        
        # delta speed is negative, meaning that we must increase speed
        else:
            #logger.debug('delta speed {} is negative ->  increase throttle'.format(delta_lin_speed))
            throttle = self.compute_throttle(delta_lin_speed, dt)
            brake = 0.0
            return throttle, brake
        
    # compute throttle based on the delta of linear speed
    def compute_throttle(self, delta_lin_speed, dt):
        """compute throttle value

        Args:
            delta_lin_speed (float): difference between targeted and actual linear speed
            dt (float): main timer clockout value

        Returns:
            float: throttle command
        """
        abs_delta_lin_speed = abs(delta_lin_speed)

        # fine tuning with delta_lin_speed to adjust the command
        return min((abs_delta_lin_speed * self.p_gain_linear_speed), LinearController.MAX_THROTTLE_CMD)

    def compute_brake(self, delta_lin_speed, target_speed):
        """compute brake

        Args:
            delta_lin_speed (float): difference between targeted and actual linear speed
            target_speed (float): targeted linear speed

        Returns:
            float: brake command
        """
        abs_delta_lin_speed = abs(delta_lin_speed)
        # if we just want to slow down a little bit at a cruise speed, we just return no brake and adjust later the throttle
        if (abs_delta_lin_speed < 0.2) and (abs(target_speed) >= 1.0): 
            #logger.debug('low delta speed and target speed normal -> no active braking')
            return 0.0
        # otherwise, active braking
        else:
            return min(abs_delta_lin_speed * self.p_gain_brake, LinearController.MAX_BRAKE_CMD)