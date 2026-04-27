#! /usr/bin/env python3

import sys
from loguru import logger
import time
import numpy as np
import copy

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from ros2_interfaces.msg import MachineIndAll, MachineSetAll
from rcl_interfaces.msg import ParameterDescriptor
from std_msgs.msg import UInt16, String
from nav_msgs.msg import Odometry

from pmi.utility.atcom_logging import PMI_logger
from pmi.machine.hal_to_machine.machine_read import MachineRead
from pmi.machine.machine_to_hal.machine_write import MachineWrite
from pmi.machine.steering_controller import SteeringController

from ros_ll_controller_python.linear_controller import LinearController
from ros_ll_controller_python.cusp_handler import CuspHandler

# main controller node
class LL_Controller(Node):

    # timer duration value for the main loop
    TIME_OPERATE_MACHINE = 0.04 # 25Hz
    # max delay to consider a command message as still valid
    # depends on the frequency of the cmd_vel publisher (10 Hz currently)
    MAX_DELAY_CMD_VEL_MSG = 0.25

    # speed constants m/s
    # used to decide how to act when switching direction FW->BW, BW->FW
    MIN_LIN_SPEED_POS = 0.1
    MIN_LIN_SPEED_NEG = -0.1
    # minimum target speed to trigger a move
    MIN_TARGET_LIN_SPEED_POS = 0.1
    MIN_TARGET_LIN_SPEED_NEG = -0.1

    def __init__(self):
        super().__init__('ll_controller_python')

        # declare params
        self.declare_parameter('p_gain_braking_ll_controller', 0.5, ParameterDescriptor(description='Proportional gain for brakes', read_only=True))
        self.declare_parameter('factor_throttle_reduction_when_not_active_braking', 0.5, ParameterDescriptor(description='Throttle reduction when a small deceleration is needed', read_only=True))
        self.declare_parameter('p_gain_linear_speed_ll_controller', 0.2, ParameterDescriptor(description='Proportional gain for linear speed', read_only=True))
        self.declare_parameter('p_gain_angular_speed_ll_controller', 0.14, ParameterDescriptor(description='Proportional gain for angular speed', read_only=True))
        self.declare_parameter('i_gain_linear_speed_ll_controller', 0.0, ParameterDescriptor(description='Integral gain for linear speed', read_only=True))
        self.declare_parameter('i_gain_angular_speed_ll_controller', 0.0, ParameterDescriptor(description='Integral gain for angular speed', read_only=True))
        self.declare_parameter('d_gain_linear_speed_ll_controller', 0.0, ParameterDescriptor(description='Derivative gain for linear speed', read_only=True))
        self.declare_parameter('d_gain_angular_speed_ll_controller', 0.0, ParameterDescriptor(description='Derivative gain for angular speed', read_only=True))
        self.declare_parameter('min_target_angular_speed_ll_controller', 0.0, ParameterDescriptor(description='Minimum target value for angular speed, below we dont move', read_only=True))
        self.declare_parameter('cmd_input_topic', '/cmd_vel_nav', ParameterDescriptor(description='Input Twist topic for LL controller command', read_only=True))

        # read parameters from launch file
        self.p_gain_brake = float(self.get_parameter('p_gain_braking_ll_controller').value)
        self.throttle_reduction_factor = float(self.get_parameter('factor_throttle_reduction_when_not_active_braking').value)
        self.p_gain_linear_speed = float(self.get_parameter('p_gain_linear_speed_ll_controller').value)
        self.p_gain = float(self.get_parameter('p_gain_angular_speed_ll_controller').value)
        self.i_gain_linear_speed = float(self.get_parameter('i_gain_linear_speed_ll_controller').value)
        self.i_gain = float(self.get_parameter('i_gain_angular_speed_ll_controller').value)
        self.d_gain_linear_speed = float(self.get_parameter('d_gain_linear_speed_ll_controller').value)
        self.d_gain = float(self.get_parameter('d_gain_angular_speed_ll_controller').value)
        self.min_target_angular_speed_ll_controller = float(self.get_parameter('min_target_angular_speed_ll_controller').value)
        self.cmd_input_topic = str(self.get_parameter('cmd_input_topic').value)
        logger.info('We got these parameters for steering : P :{} D : {} I : {}'.format(self.p_gain, self.d_gain, self.i_gain))

        # memorized messages
        self.mem_cmd_vel = None
        self.mem_machine_ind_all = None
        # memorized timestamp of the latest command message
        self.mem_time_latest_cmd_vel_received = None
        # flag to reset values only once per end of path
        self.has_been_reset = True

        # init CuspHandler
        self.cusp_handler = CuspHandler()

        # prepared write messages
        """
        defaults to undef, but the write_bridge has one message memorized,
        with all options disabled except parking_brake,
        and is in neutral, automatic, no throttle,
        but 100% brake.
        so better change these values before trying to move !
        """
        self.machine_set_all = MachineSetAll()
        # heartbeat counter
        self.cnt_heartbeat = 0

        # specific controllers setup
        self.linear_controller = LinearController()
        self.steering_controller = SteeringController()
        self.linear_controller.set_up(self.throttle_reduction_factor, self.p_gain_linear_speed, self.p_gain_brake)
        self.steering_controller.set_up(self.p_gain, self.i_gain, self.d_gain)

    def start(self):
        """ start method
        """
        # start timer and subscribers/publishers
        self.sub_cmd_vel = self.create_subscription(Twist, self.cmd_input_topic, self.cb_cmd_vel, 1)
        self.sub_machine_ind_all = self.create_subscription(MachineIndAll,'/atcom_wa380/wheeler/read/all', self.cb_machine_ind_all, 1)
        self.pub_machine_set_all = self.create_publisher(MachineSetAll, '/atcom_wa380/wheeler/write/nav_ctrl', 1)
        self.pub_heartbeat = self.create_publisher(UInt16, '/atcom_wa380/wheeler/write/nav_heartbeat', 1)

        # timer for operating loop
        self.create_timer(LL_Controller.TIME_OPERATE_MACHINE, self.operate_machine)

    def reset_at_end_of_path(self):
        """ reset when arrived at the end of the path
        """
        # memorized values
        self.mem_cmd_vel = None
        self.mem_machine_ind_all = None
        self.mem_time_latest_cmd_vel_received = None

        # prepared write messages
        self.machine_set_all = MachineSetAll()

        # heartbeat counter
        self.cnt_heartbeat = 0

        # memory target steering angles
        logger.info('end of path')

    def cb_cmd_vel(self, msg):
        """Callback of the configured command topic subscriber.

        Args:
            msg (Twist): Message containing linear and angular velocities, as well as custom data.
        """
        logger.info('Twist Msg : lin.x {}; dist_end_path {}; lookahead {}; dist_cusp {}; curv {}; ang.z {}'.format(
            msg.linear.x,
            msg.linear.y,
            msg.linear.z,
            msg.angular.x,
            msg.angular.y,
            msg.angular.z
        ))
        
        # memorize data and timestamp
        self.mem_cmd_vel = msg
        self.mem_time_latest_cmd_vel_received = time.time()

    def cb_machine_ind_all(self, msg):
        """callback of the /atcom_wa380/wheeler/read/all

        Args:
            msg (MachineIndAll): Message containing all data from machine such as speed, steering_angle, ...
        """
        #logger.debug('MachineIndall : {}'.format(msg))
        # memorize
        self.mem_machine_ind_all = msg

    def publish(self):
        """publish latest commands to the machine as well as the heartbeart
        """
        self.pub_machine_set_all.publish(self.machine_set_all)
        self.publish_heartbeat()
    
    def publish_heartbeat(self):
        """publish heartbeat message
        """
        hb = UInt16()
        hb.data = self.cnt_heartbeat
        self.pub_heartbeat.publish(hb)
        #logger.debug('pub heartbeat : {}'.format(self.cnt_heartbeat))
        self.cnt_heartbeat = (self.cnt_heartbeat + 1) % 65535

    # machine set up
    def set_machine(self, throttle, brake, dm, parking_brake, steering):
        """prepare and publish commands to the machine

        Args:
            throttle (float): throttle value [0.0, 1.0]
            brake (float): brake value [0.0, 1.0]
            dm (int): directional mode : FW = MachineWrite.DM_FORWARD, BW = MachineWrite.DM_REVERSE, NTRL = MachineWrite.DM_NEUTRAL
            parking_brake (bool): parking brake, True = MachineWrite.MachineWriteOptions.PARKING_BRAKE_ENABLE, False = MachineWrite.MachineWriteOptions.PARKING_BRAKE_DISABLE
            steering (float): steering value [-1.0, 1.0]
        """

        # setup msg
        self.machine_set_all.throttle = throttle
        self.machine_set_all.brake = brake
        self.machine_set_all.steering = steering
        self.machine_set_all.directional_sel = dm
        self.machine_set_all.options.parking_brake = parking_brake

        # publish msg
        logger.debug('pub : t : {}, b : {}, dm : {}, p_b : {}, st : {}'.format(throttle, brake, dm, parking_brake, steering))
        #logger.debug(self.machine_set_all)
        self.publish()

    def set_idle(self, mem_machine_ind_all):
        """set the machine in idle mode

        Args:
            mem_machine_ind_all (MachineIndAll): memorized message containing machine data
        """
        # if the machine state is unknown, we go to idle with active braking, but no parking brake, as we could be moving and this would destroy the parking brake
        if (mem_machine_ind_all == None):
            logger.debug('mem_machine_ind_all None -> machine state unknown...')
            self.set_machine(throttle=0.0, brake=0.3, dm=MachineWrite.DM_NEUTRAL, parking_brake=MachineWrite.MachineWriteOptions.PARKING_BRAKE_DISABLE, steering=0.0)
            return 
        
        # operating stop when we are moving
        if abs(mem_machine_ind_all.speed) > 0.2:
            logger.debug('speed is too big -> operate_stop()')
            self.operate_stop(delta_lin_speed=-1.0 * mem_machine_ind_all.speed, steering=0.0, target_speed=0.0)
            return
        
        # orientate the machine straight before going to idle
        if abs(mem_machine_ind_all.steering_angle) > 3:
            logger.debug('too much steering -> orientate')
            self.oriente_before_idle(LL_Controller.TIME_OPERATE_MACHINE, mem_machine_ind_all)
            return
        
        # idle with parking brake enabled as we are sure to be stopped
        self.set_machine(throttle=0.0, brake=0.3, dm=MachineWrite.DM_NEUTRAL, parking_brake=MachineWrite.MachineWriteOptions.PARKING_BRAKE_ENABLE, steering=0.0)
        #logger.info('Setting parking brake ON, machine is idle')
        
    # operate machine
    def operate_FW_acc_dec(self, delta_lin_speed, steering, lin_speed_machine, dt, target_speed, mem_machine_ind_all, are_we_at_the_cusp):
        """operate the machine in the forward direction

        Args:
            delta_lin_speed (float): difference between the target linear speed and the current linear speed
            steering (float): steering value computed before in the operate_machine() method
            lin_speed_machine (float): linear speed of the machine
            dt (float): timer clock value
            target_speed (float): targeted linear speed value
            mem_machine_ind_all (MachineIndAll): machine's data
            are_we_at_the_cusp (bool): flag to know whether we are at the cusp or not
        """
        #logger.debug('operate_FW_acc_dec')

        # compute brake and throttle
        throttle, brake = self.linear_controller.compute_throttle_brake_FW(delta_lin_speed, dt, target_speed)
        
        # shift to neutral only if active braking and we are slow enough, otherwise we use the motor brake
        if (brake > 0.0) and (lin_speed_machine < 0.5):
            logger.debug('shift to neutral because active braking and almost stopped')
            dm = MachineWrite.DM_NEUTRAL
        else:
            dm = MachineWrite.DM_FORWARD
        parking_brake = MachineWrite.MachineWriteOptions.PARKING_BRAKE_DISABLE

        # if at cusp, we stay still to let time to adapt steering to new direction
        if are_we_at_the_cusp:
            logger.debug('at the cusp -> cant move for a delay, only steering')
            self.set_machine(0.1, LinearController.BRAKE_USUAL_VALUE, MachineWrite.DM_NEUTRAL, parking_brake, steering)
        # normal behavior otherwise
        else:
            self.set_machine(throttle, brake, dm, parking_brake, steering)
        
    def operate_BW_acc_dec(self, delta_lin_speed, steering, lin_speed_machine, dt, target_speed, mem_machine_ind_all, are_we_at_the_cusp):
        """operate the machine in the backward direction

        Args:
            delta_lin_speed (float): difference between the target linear speed and the current linear speed
            steering (float): steering value computed before in the operate_machine() method
            lin_speed_machine (float): linear speed of the machine
            dt (float): timer clock value
            target_speed (float): targeted linear speed value
            mem_machine_ind_all (MachineIndAll): machine's data
            are_we_at_the_cusp (bool): flag to know whether we are at the cusp or not
        """
        #logger.debug('operate_BW_acc_dec')

        # compute brake and throttle
        throttle, brake = self.linear_controller.compute_throttle_brake_BW(delta_lin_speed, dt, target_speed)
        
        # shift to neutral only if active braking and if we're slow enough, otherwise we use the motor brake
        if (brake > 0.0) and (lin_speed_machine > -0.5):
            logger.debug('shift to neutral because active braking and almost stopped')
            dm = MachineWrite.DM_NEUTRAL
        else:
            dm = MachineWrite.DM_REVERSE
        parking_brake = MachineWrite.MachineWriteOptions.PARKING_BRAKE_DISABLE

        # if at cusp, we stay still to let time to adapt steering to new direction
        if are_we_at_the_cusp:
            logger.debug('at the cusp -> cant move for a delay, only steering')
            self.set_machine(0.1, LinearController.BRAKE_USUAL_VALUE, MachineWrite.DM_NEUTRAL, parking_brake, steering)
        # normal behavior otherwise
        else:
            self.set_machine(throttle, brake, dm, parking_brake, steering)

    def operate_stop(self, delta_lin_speed, steering, target_speed):
        """operate a stop by computing brake command and dealing gearbox directional mode

        Args:
            delta_lin_speed (float): difference between target linear speed and actual linear speed
            steering (float): steering command value, computed by operate_machine()
            target_speed (float): target linear speed
        """
        logger.debug('operate_stop')
        throttle = 0.0
        brake = self.linear_controller.compute_brake(delta_lin_speed, target_speed)
        # since we want to change direction or fully stop, we want to at least brake the usual value
        brake = max(brake, LinearController.BRAKE_USUAL_VALUE)
        # shift to neutral because we stay in active braking no matter what
        dm = MachineWrite.DM_NEUTRAL
        parking_brake = MachineWrite.MachineWriteOptions.PARKING_BRAKE_DISABLE
        self.set_machine(throttle, brake, dm, parking_brake, steering)

    def round(self, val):
        """round a float value to two decimal digits

        Args:
            val (float): input value

        Returns:
            float: return rounded value
        """
        return (int(val * 100.0)) / 100.0
    
    def oriente_before_idle(self, dt, mem_machine_ind_all):
        """orientate the machine toward 0 deg steering angle

        Args:
            dt (float): timer clock value
            mem_machine_ind_all (MachineIndAll): machine data
        """
        logger.debug('orientating machine at the end')
        # compute steering command
        steering = self.steering_controller.compute_steering_on_angle(mem_machine_ind_all, dt, 0.0) 
        # reduce steering command since we are not moving (not sure if that is still required)
        steering = steering / 2.0
        self.set_machine(0.1, 0.1, MachineWrite.DM_NEUTRAL, MachineWrite.MachineWriteOptions.PARKING_BRAKE_DISABLE, steering)

    def operate_machine(self):
        """main function called after clockout of the main timer
        """
        #logger.debug('TIMEOUT -> operate_machine()')

        # make sure all required values are valid, otherwise go to idle
        if (self.mem_machine_ind_all == None) or (self.mem_time_latest_cmd_vel_received == None) or (self.mem_cmd_vel == None):
            logger.debug('cant operate machine, None value...')
            self.set_idle(self.mem_machine_ind_all)
            return
        
        # deepcopy to have local variable in case it changes in another callback during this execution
        mem_cmd_vel = copy.deepcopy(self.mem_cmd_vel)
        mem_machine_ind_all = copy.deepcopy(self.mem_machine_ind_all)
        time_last_cmd_vel_received = copy.deepcopy(self.mem_time_latest_cmd_vel_received)
        
        # make sure the latest command message is not too old
        delta_tm_msg = time.time() - time_last_cmd_vel_received

        # normal case, msg must arrive within 0.2s
        if delta_tm_msg <= LL_Controller.MAX_DELAY_CMD_VEL_MSG:
            logger.debug('NEW CYCLE !')

        # backup msg are published each 0.5s
        elif (mem_cmd_vel.linear.x == -1.0) and (mem_cmd_vel.angular.z == 0.0) \
            and (delta_tm_msg <= 0.6):
            logger.debug('NEW CYCLE BACK-UP MSG')

        # too old and not backup
        else:
            logger.warning('dt {} too big -> IDLE'.format(delta_tm_msg))
            self.set_idle(self.mem_machine_ind_all)
            # if not reset so far, then reset
            if self.has_been_reset == False:
                self.reset_at_end_of_path()
                self.has_been_reset = True
            return
        
        # delta time
        dt = LL_Controller.TIME_OPERATE_MACHINE

        # reset flag
        self.has_been_reset = False

        # get input data
        flag_speed_direction_unknown = mem_machine_ind_all.flag_speed_signing_uncertain
        lin_speed_machine = mem_machine_ind_all.speed
        distance_to_end_path = mem_cmd_vel.linear.y
        distance_to_cusp = mem_cmd_vel.angular.x

        # compute flags : end of path, cusp
        arriving_at_end_of_path = True if ((distance_to_cusp == -1.0) and (distance_to_end_path < 3.0)) else False
        self.cusp_handler.update_distance_to_next_cusp(distance_to_cusp, lin_speed_machine, dt)
        are_we_at_the_cusp = self.cusp_handler.get_currently_at_cusp()

        # now that we have all required flags, lets deal with targets !
        # compute targets and deltas
        target_lin_speed = mem_cmd_vel.linear.x
        delta_lin_speed = target_lin_speed - lin_speed_machine

        # compute target steering angle based on the curvature of the lookahead arc
        target_steering_angle = self.steering_controller.compute_target_steering_angle(mem_cmd_vel)
        logger.debug('curvature is {}, target steering angle is {}', mem_cmd_vel.angular.y, target_steering_angle)

        # compute steering sign and intensity
        steering = 0.0

        # if speed sign is unknown and we are not at a cusp -> steering = 0.0 always
        if (flag_speed_direction_unknown == True) and (are_we_at_the_cusp == False):
            steering = 0.0
            logger.debug('Due to positive flag to unknown speed, steering is 0.0')
        else:
            # when at the cusp, we fix target steering angle to 0.0
            # in the future, we might want to steer at the opposite direction of what we did before the cusp
            if are_we_at_the_cusp == True:
                target_steering_angle = 0.0
                logger.debug('fixing target_steering_angle at cusp : {}'.format(target_steering_angle))

            # when at the end of path -> we want to have the machine straight
            elif arriving_at_end_of_path == True:
                target_steering_angle = 0.0
                logger.debug('at the end of path, target_steering_angle : {}'.format(target_steering_angle))

            # normal case
            else:
                # compute sign, depending on linear speed sign and angular velocity sign
                target_steering_angle = self.steering_controller.compute_sign_target_steering_angle(mem_cmd_vel, lin_speed_machine) * target_steering_angle
                # update rolling average of the target steering angle
                target_steering_angle = self.steering_controller.get_filtered_target_steering_angle(target_steering_angle, dt)
            
            # compute steering command for cusp, end of path and normal case
            steering = self.steering_controller.compute_steering_on_angle(mem_machine_ind_all, dt, target_steering_angle)       
    
        # we want to move FW, targeted speed is positive and greater than 0.1m/s
        logger.debug('target lin speed : {}, current lin speed : {}'.format(target_lin_speed, lin_speed_machine))
        if target_lin_speed > LL_Controller.MIN_TARGET_LIN_SPEED_POS:
            #logger.debug('we want to move FW')

            # we are moving BW -> need to stop first, and only afterwards accelerating FW
            if lin_speed_machine < LL_Controller.MIN_LIN_SPEED_NEG:
                #logger.debug('we are moving BW -> braking')
                self.operate_stop(delta_lin_speed, steering, target_lin_speed)
                return
            
            # we are already moving FW, can be accelerating or decelerating FW
            else:
                #logger.debug('we are stopped or already moving FW')
                self.operate_FW_acc_dec(delta_lin_speed, steering, lin_speed_machine, dt, target_lin_speed, mem_machine_ind_all, are_we_at_the_cusp)
                return

        # we want to move BW
        elif target_lin_speed < LL_Controller.MIN_TARGET_LIN_SPEED_NEG:
            #logger.debug('we want to move BW')

            # we are moving FW -> need to stop first, and only afterwards accelerating BW
            if lin_speed_machine > LL_Controller.MIN_LIN_SPEED_POS :
                #logger.debug('we are moving FW -> braking')
                self.operate_stop(delta_lin_speed, steering, target_lin_speed)
                return

            # we are already moving BW, can be accelerating or decelerating BW
            else:
                #logger.debug('we are stopped or already moving BW')
                self.operate_BW_acc_dec(delta_lin_speed, steering, lin_speed_machine, dt, target_lin_speed, mem_machine_ind_all, are_we_at_the_cusp)
                return

        # targeted speed is too low, we don't move
        else:
            #logger.info('targeted speed is too small, we dont move.')
            if (abs(lin_speed_machine) < 0.2) and (abs(steering) < 0.05):
                #logger.debug('machine speed : {}, steering : {} -> lets go to IDLE'.format(lin_speed_machine, steering))
                self.set_idle(self.mem_machine_ind_all)
                return
            else:
                #logger.debug('machine speed is too big to go to IDLE or we are steering -> active braking first')
                self.operate_stop(delta_lin_speed, steering, target_lin_speed)
                return


def main():
    rclpy.init()
    controller = LL_Controller()
    controller.start()

    pmi_logger = PMI_logger('INFO', 'DEBUG', '~/Desktop/AlpineR/alpiner_ros2/ros2_ws/log_atcom/ll_controller_{time}.log')
    #pmi_logger = PMI_logger('INFO', 'DEBUG', '/home/sellig/work/ros2_ws/log/ll_controller_{time}.log')

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        print('KeyboardInterrupt caught, shutting down controller...')
    finally:
        try:    
            controller.destroy_node()
        except Exception as e:
            print('Error while destroying controller : {}'.format(e))
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
