from ros_ll_controller_python import controller
from loguru import logger

if __name__ == "__main__":
    test_0 = True
    test_1 = True
    test_2 = True
    test_3 = True
    test_4 = False

    if test_0:
        logger.info('Test 0 : compute_brake()')
        for i in range(-100, 100):
            f = i/10.0 # delta_lin_speed from -10m/s to 10m/s
            brake = controller.LL_Controller.compute_brake(delta_lin_speed=f)
            logger.info('delta_lin_speed = {} -> brake is {}'.format(f, brake))

    if test_1:
        logger.info('Test 1 : compute_throttle()')
        for i in range(-100, 100):
            f = i/10.0 # delta_lin_speed from -10m/s to 10m/s
            throttle = controller.LL_Controller.compute_throttle(delta_lin_speed=f, gain_linear_speed=0.2)
            logger.info('delta_lin_speed = {} -> throttle is {}'.format(f, throttle))

    if test_2:
        logger.info('Test 2 : compute_throttle_brake_FW()')
        for i in range(-100, 100):
            f = i/10.0 # delta_lin_speed from -10m/s to 10m/s
            throttle, brake = controller.LL_Controller.compute_throttle_brake_FW(delta_lin_speed=f, gain_linear_speed=0.2)
            logger.info('delta_lin_speed = {} -> throttle is {}, brake is {}'.format(f, throttle, brake))

    if test_3:
        logger.info('Test 3 : compute_throttle_brake_BW()')
        for i in range(-100, 100):
            f = i/10.0 # delta_lin_speed from -10m/s to 10m/s
            throttle, brake = controller.LL_Controller.compute_throttle_brake_BW(delta_lin_speed=f, gain_linear_speed=0.2)
            logger.info('delta_lin_speed = {} -> throttle is {}, brake is {}'.format(f, throttle, brake))