from loguru import logger
import json

from pmi.utility.edges import EdgeDetection
from pmi.machine.machine_to_hal.machine_write import MachineWrite

class MachineLogic:

    # changes, basically a copy from the constants in class EdgeDetection, copied and renamed for more clarity here in this class
    TOGGLE = EdgeDetection.RISING_EDGE_POS
    UNCHANGED = EdgeDetection.NO_EDGE
    GEAR_SPEED_UPSHIFT = EdgeDetection.RISING_EDGE_POS
    GEAR_SPEED_DOWNSHIFT = EdgeDetection.RISING_EDGE_NEG
    SM_TO_HIGH = EdgeDetection.RISING_EDGE_POS
    SM_TO_LOW = EdgeDetection.RISING_EDGE_NEG
    FW_SHIFT = EdgeDetection.RISING_EDGE_POS
    REV_SHIFT = EdgeDetection.RISING_EDGE_NEG
    HORN_START = EdgeDetection.RISING_EDGE_POS
    HORN_STOP = EdgeDetection.FALLING_EDGE_POS
    KICKDOWN_START = EdgeDetection.RISING_EDGE_POS
    KICKDOWN_STOP = EdgeDetection.FALLING_EDGE_POS
    TM_CUTOFF_START = EdgeDetection.RISING_EDGE_POS
    TM_CUTOFF_STOP = EdgeDetection.FALLING_EDGE_POS
    PPC_LOCK_RELEASE_START = EdgeDetection.RISING_EDGE_POS
    PPC_LOCK_RELEASE_STOP = EdgeDetection.FALLING_EDGE_POS
    DISABLE_FRONT_LIDAR_START = EdgeDetection.RISING_EDGE_POS
    DISABLE_FRONT_LIDAR_STOP = EdgeDetection.FALLING_EDGE_POS

    def __init__(self):
        """
        __init__ Constructor, the attributes are by default initialized to constants.
        """
        self.gear_speed = MachineWrite.GS_1ST
        self.shiftmode = MachineWrite.SM_LOW
        self.directional_mode = MachineWrite.DM_NEUTRAL
        self.kickdown = MachineWrite.MachineWriteOptions.KICK_DOWN_DISABLE
        self.autodig = MachineWrite.MachineWriteOptions.AUTO_DIG_DISABLE
        self.horn = MachineWrite.MachineWriteOptions.HORN_DISABLE
        self.lights = MachineWrite.MachineWriteOptions.LIGHTS_DISABLE
        self.cutoff_tm = MachineWrite.MachineWriteOptions.TM_CUTOFF_DISABLE
        self.shifthold = MachineWrite.MachineWriteOptions.SHIFT_HOLD_SWITCH_DISABLE
        self.ecss = MachineWrite.MachineWriteOptions.ECSS_DISABLE
        self.parking_brake = MachineWrite.MachineWriteOptions.PARKING_BRAKE_ENABLE
        self.ppc_lock_release = MachineWrite.PPC_LOCK_RELEASE_DISABLE
        self.disable_front_lidar = MachineWrite.FRONT_LIDAR_ENABLE
        self.throttle = 0.0
        self.brake = 0.0
        self.boom = 0.0
        self.bucket = 0.0
        self.steering = 0.0

    def __str__(self):
        return 'MachineLogic : \n\tgear speed : {}\n\tshiftmode : {}\n\tdir mode : {}\n\tkickdown : {}\n\tautodig : {} \
            \n\thorn : {}\n\tlights : {}\n\tcutoff tm : {}\n\tshifthold : {}\n\tecss : {}\n\tparking brake : {}\n\tthrottle : {}\n\tbrake : {} \
            \n\tboom : {}\n\tbucket : {}\n\tsteering : {}\n\tppc : {}\n\tdisable front lidar : {}'.format(
                self.gear_speed,
                self.shiftmode,
                self.directional_mode,
                self.kickdown,
                self.autodig,
                self.horn, 
                self.lights, 
                self.cutoff_tm,
                self.shifthold, 
                self.ecss, 
                self.parking_brake, 
                self.throttle, 
                self.brake,
                self.boom,
                self.bucket, 
                self.steering,
                self.ppc_lock_release,
                self.disable_front_lidar
            )

    def update(self, gear_cmd, forward_reverse_cmd, shiftmode_cmd, \
        neutral_cmd, kickdown_cmd, autodig_cmd, horn_cmd, lights_cmd, \
            cutoff_tm_cmd, shifthold_cmd, ecss_cmd, parking_brake_cmd, throttle_cmd, brake_cmd, \
                boom_cmd, bucket_cmd, steering_cmd, ppc_cmd, disable_front_lidar_cmd):
        """
        update Update the machine logic with commands from the inputs

        :param gear_cmd: gear speed command
        :type gear_cmd: Int, expected value : MachineLogic.GEAR_SPEED_UPSHIFT or MachineLogic.GEAR_SPEED_DOWNSHIFT or MachineLogic.UNCHANGED
        :param forward_reverse_cmd: directional mode command
        :type forward_reverse_cmd: Int, expected value : MachineLogic.REV_SHIFT or MachineLogic.FW_SHIFT or MachineLogic.UNCHANGED
        :param shiftmode_cmd: shiftmode command for manual-low-high
        :type shiftmode_cmd: MachineLogic.SM_TO_HIGH or MachineLogic.SM_TO_LOW or MachineLogic.UNCHANGED
        :param neutral_cmd: neutral preselect command
        :type neutral_cmd: Int, expected value : MachineLogic.TOGGLE or MachineLogic.UNCHANGED
        :param kickdown_cmd: kickdown command
        :type kickdown_cmd: Int, expected value : MachineLogic.KICKDOWN_START or MachineLogic.KICKDOWN_STOP
        :param autodig_cmd: autodig command
        :type autodig_cmd: Int, expected value : MachineLogic.TOGGLE or MachineLogic.UNCHANGED
        :param horn_cmd: horn command
        :type horn_cmd: Int, expected value : MachineLogic.HORN_START or MachineLogic.HORN_STOP
        :param lights_cmd: lights command
        :type lights_cmd: Int, expected value : MachineLogic.TOGGLE or MachineLogic.UNCHANGED
        :param cutoff_tm_cmd: cutoff TM command
        :type cutoff_tm_cmd: Int, expected value : MachineLogic.TM_CUTOFF_START or MachineLogic.TM_CUTOFF_STOP
        :param shifthold_cmd: shifthold command
        :type shifthold_cmd: Int, expected value : MachineLogic.TOGGLE or MachineLogic.UNCHANGED
        :param ecss_cmd: ECSS command
        :type ecss_cmd: Int, expected value : MachineLogic.TOGGLE or MachineLogic.UNCHANGED
        :param parking_brake_cmd: parking brake command
        :type parking_brake_cmd: Int, expected value : MachineLogic.TOGGLE or MachineLogic.UNCHANGED
        :param throttle_cmd: throttle command
        :type throttle_cmd: Float, expected range : [0.0..1.0]
        :param brake_cmd: Brake command
        :type brake_cmd: Float, expected range : [0.0..1.0]
        :param boom_cmd: Boom command
        :type boom_cmd: Float, expected range : [-1.0..1.0]
        :param bucket_cmd: Bucket command
        :type bucket_cmd: Float, expected range : [-1.0..1.0]
        :param steering_cmd: Steering
        :type steering_cmd: Float, expected range : [-1.0..1.0]
        :param ppc_cmd: PPC
        :type ppc_cmd: Boolean
        :param disable_front_lidar_cmd: Disable front lidar
        :type disable_front_lidar_cmd: Int, expected value : MachineLogic.DISABLE_FRONT_LIDAR_START or MachineLogic.DISABLE_FRONT_LIDAR_STOP
        """

        # gear speed
        if (self.gear_speed < MachineWrite.GS_4TH) and (gear_cmd == MachineLogic.GEAR_SPEED_UPSHIFT):
            #self.gear_speed += 1
            logger.debug('TODO : unchanged GS, would be : gear up shifted : {}'.format(self.gear_speed))
        elif (self.gear_speed > MachineWrite.GS_1ST) and (gear_cmd == MachineLogic.GEAR_SPEED_DOWNSHIFT):
            #self.gear_speed -= 1
            logger.debug('TODO : unchanged GS, would be : gear down shifted : {}'.format(self.gear_speed))

        # shiftmode manual-low-high
        if (shiftmode_cmd == MachineLogic.SM_TO_HIGH) and (self.shiftmode == MachineWrite.SM_LOW):
            self.shiftmode = MachineWrite.SM_HIGH
            logger.debug('shiftmode toggled to HIGH: {}'.format(self.shiftmode))
        elif (shiftmode_cmd == MachineLogic.SM_TO_LOW) and (self.shiftmode == MachineWrite.SM_HIGH):
            self.shiftmode = MachineWrite.SM_LOW
            logger.debug('shiftmode toggled to LOW: {}'.format(self.shiftmode))
        else :
            logger.debug('shiftmode untoggled: {}, cmd is : {}'.format(self.shiftmode, shiftmode_cmd))

        # directional mode
        # mode FORWARD or REVERSE to NEUTRAL
        if ((self.directional_mode == MachineWrite.DM_FORWARD) or (self.directional_mode == MachineWrite.DM_REVERSE)) and (neutral_cmd == MachineLogic.TOGGLE):
            self.directional_mode = MachineWrite.DM_NEUTRAL
            logger.debug('directional mode to neutral : {}'.format(self.directional_mode))
        
        # mode FORWARD or NEUTRAL to REVERSE
        elif ((self.directional_mode == MachineWrite.DM_FORWARD) or (self.directional_mode == MachineWrite.DM_NEUTRAL)) and (forward_reverse_cmd == MachineLogic.REV_SHIFT):
            self.directional_mode = MachineWrite.DM_REVERSE
            logger.debug('directional mode to reverse : {}'.format(self.directional_mode))

        # mode REVERSE or NEUTRAL to FORWARD
        elif ((self.directional_mode == MachineWrite.DM_REVERSE) or (self.directional_mode == MachineWrite.DM_NEUTRAL)) and (forward_reverse_cmd == MachineLogic.FW_SHIFT):
            self.directional_mode = MachineWrite.DM_FORWARD
            logger.debug('directional mode to forward : {}'.format(self.directional_mode))

        # kickdown, maintained as long as the button is pressed
        if kickdown_cmd == MachineLogic.KICKDOWN_START:
            self.kickdown = MachineWrite.MachineWriteOptions.KICK_DOWN_ENABLE
            logger.debug('kickdown started : {}'.format(self.kickdown))
        elif kickdown_cmd == MachineLogic.KICKDOWN_STOP:
            self.kickdown = MachineWrite.MachineWriteOptions.KICK_DOWN_DISABLE
            logger.debug('kickdown stopped : {}'.format(self.kickdown))
        
        # autodig, toggle, maintained until next push
        if autodig_cmd == MachineLogic.TOGGLE:
            self.autodig = not self.autodig
            logger.debug('autodig toggled : {}'.format(self.autodig))

        # horn, maintained as long as the button is pressed
        if horn_cmd == MachineLogic.HORN_START:
            self.horn = MachineWrite.MachineWriteOptions.HORN_ENABLE
            logger.debug('horn turned on : {}'.format(self.horn))
        elif horn_cmd == MachineLogic.HORN_STOP:
            self.horn = MachineWrite.MachineWriteOptions.HORN_DISABLE
            logger.debug('horn turned off : {}'.format(self.horn))

        # lights, toggle, maintained until next push
        if lights_cmd == MachineLogic.TOGGLE:
            self.lights = not self.lights
            logger.debug('lights toggled : {}'.format(self.lights))

        # cutoff tm, maintained as long as the button is pressed
        if cutoff_tm_cmd == MachineLogic.TM_CUTOFF_START:
            self.cutoff_tm = MachineWrite.MachineWriteOptions.TM_CUTOFF_ENABLE
            logger.debug('cutoff_tm started : {}'.format(self.cutoff_tm))
        elif cutoff_tm_cmd == MachineLogic.TM_CUTOFF_STOP:
            self.cutoff_tm = MachineWrite.MachineWriteOptions.TM_CUTOFF_DISABLE
            logger.debug('cutoff_tm stopped : {}'.format(self.cutoff_tm))

        # shifthold, toggle, maintained until next push
        if shifthold_cmd == MachineLogic.TOGGLE:
            self.shifthold = not self.shifthold
            logger.debug('shifthold toggled : {}'.format(self.shifthold))

        # ecss, toggle, maintained until next push
        if ecss_cmd == MachineLogic.TOGGLE:
            self.ecss = not self.ecss
            logger.debug('ecss toggled : {}'.format(self.ecss))

        # parking brake, toggle, maintained until next push
        if parking_brake_cmd == MachineLogic.TOGGLE:
            self.parking_brake = not self.parking_brake
            logger.debug('parking_brake toggled : {}'.format(self.parking_brake))

        # ppc, maintained as long as the button is pressed
        if ppc_cmd == MachineLogic.PPC_LOCK_RELEASE_START:
            self.ppc_lock_release = MachineWrite.PPC_LOCK_RELEASE_ENABLE
            logger.debug('ppc turned on : {}'.format(self.ppc_lock_release))
        elif ppc_cmd == MachineLogic.PPC_LOCK_RELEASE_STOP:
            self.ppc_lock_release = MachineWrite.PPC_LOCK_RELEASE_DISABLE
            logger.debug('ppc turned off : {}'.format(self.ppc_lock_release))

        # disable front lidar, maintained as long as button in pressed here, but in reality, longer due to timer in safety SPS
        if disable_front_lidar_cmd == MachineLogic.DISABLE_FRONT_LIDAR_START:
            self.disable_front_lidar = MachineWrite.FRONT_LIDAR_DISABLE
            logger.info('front lidar disabled : {}'.format(self.disable_front_lidar))
        elif disable_front_lidar_cmd == MachineLogic.DISABLE_FRONT_LIDAR_STOP:
            self.disable_front_lidar = MachineWrite.FRONT_LIDAR_ENABLE
            logger.info('front lidar enabled (after timeout in PLC) : {}'.format(self.disable_front_lidar))

        # axis
        self.throttle = throttle_cmd
        logger.debug('throttle : {}'.format(throttle_cmd))
        self.brake = brake_cmd
        logger.debug('brake : {}'.format(brake_cmd))
        self.boom = boom_cmd
        logger.debug('boom : {}'.format(boom_cmd))
        self.bucket = bucket_cmd
        logger.debug('bucket : {}'.format(bucket_cmd))
        self.steering = steering_cmd
        logger.debug('steering : {}'.format(steering_cmd))
        logger.debug(self)

    def to_json(self):
        """
        to_json convert this object to a JSON string

        :return: JSON representation of this object
        :rtype: Str
        """
        msg= {
            'gear_speed':self.gear_speed,
            'shift_mode':self.shiftmode,
            'directional_mode':self.directional_mode,
            'kickdown':self.kickdown,
            'autodig':self.autodig,
            'horn':self.horn,
            'lights':self.lights,
            'cutoff_tm':self.cutoff_tm,
            'shifthold':self.shifthold,
            'ecss':self.ecss,
            'parking_brake':self.parking_brake,
            'throttle':self.throttle,
            'brake':self.brake,
            'boom':self.boom,
            'bucket':self.bucket,
            'steering':self.steering,
            'ppc':self.ppc_lock_release,
            'disable_front_lidar':self.disable_front_lidar
        }
        return json.dumps(msg)

    def to_machine_write(self):
        """
        to_machine_write convert this object to a MachineWrite object

        :return: converted object
        :rtype: MachineWrite
        """
        return MachineWrite(
            self.gear_speed,
            self.shiftmode,
            self.directional_mode,
            MachineWrite.MachineWriteOptions(
                self.parking_brake,
                self.ecss,
                self.shifthold,
                self.cutoff_tm,
                self.lights,
                self.horn,
                self.autodig,
                self.kickdown
            ),
            self.throttle,
            self.brake,
            self.boom, 
            self.bucket,
            self.steering,
            self.ppc_lock_release,
            self.disable_front_lidar
        )