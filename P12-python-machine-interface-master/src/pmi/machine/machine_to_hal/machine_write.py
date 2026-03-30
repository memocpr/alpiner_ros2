from loguru import logger

class MachineWrite:

    # constants to be used in machine world and ROS world
    GS_1ST = 1
    GS_2ND = 2
    GS_3RD = 3
    GS_4TH = 4
    SM_LOW = 5
    SM_MANUAL = 6
    SM_HIGH = 7
    DM_FORWARD = 8
    DM_REVERSE = 9
    DM_NEUTRAL = 10
    PPC_LOCK_RELEASE_ENABLE = True
    PPC_LOCK_RELEASE_DISABLE = False
    FRONT_LIDAR_DISABLE = True
    FRONT_LIDAR_ENABLE = False
    DEFAULT_BRAKE = 0.6

    class MachineWriteOptions:

        # constants to be used in machine world and ROS world
        PARKING_BRAKE_ENABLE = True
        PARKING_BRAKE_DISABLE = False
        ECSS_ENABLE = True
        ECSS_DISABLE = False
        SHIFT_HOLD_SWITCH_ENABLE = True
        SHIFT_HOLD_SWITCH_DISABLE = False
        TM_CUTOFF_ENABLE = True
        TM_CUTOFF_DISABLE = False
        LIGHTS_ENABLE = True
        LIGHTS_DISABLE = False
        HORN_ENABLE = True
        HORN_DISABLE = False
        AUTO_DIG_ENABLE = True
        AUTO_DIG_DISABLE = False
        KICK_DOWN_ENABLE = True
        KICK_DOWN_DISABLE = False
        
        def __init__(self, parking_brake, ecss_active, shift_hold_switch, tm_cutoff, lights, horn, auto_dig, kick_down):
            """
            __init__ Create an object that represents the write options, encoded in the register 1's MSB

            :param parking_brake: enable/disable parking brake,
            :type parking_brake: boolean, expected value : MachineWrite.MachineWriteOptions.PARKING_BRAKE_ENABLE or MachineWrite.MachineWriteOptions.PARKING_BRAKE_DISABLE
            :param ecss_active: enable/disable ECSS (Electronic Control Suspension System)
            :type ecss_active: boolean, expected value : MachineWrite.MachineWriteOptions.ECSS_ENABLE or MachineWrite.MachineWriteOptions.ECSS_DISABLE
            :param shift_hold_switch: block automatically upshifts 
            :type shift_hold_switch: boolean, expected value MachineWrite.MachineWriteOptions.SHIFT_HOLD_SWITCH_ENABLE or MachineWrite.MachineWriteOptions.SHIFT_HOLD_SWITCH_DISABLE
            :param tm_cutoff: shift gear to Neutral with parking brake
            :type tm_cutoff: boolean, expected value : MachineWrite.MachineWriteOptions.TM_CUTOFF_ENABLE or MachineWrite.MachineWriteOptions.TM_CUTOFF_DISABLE
            :param lights: lights
            :type lights: boolean, expected value : MachineWrite.MachineWriteOptions.LIGHTS_ENABLE or MachineWrite.MachineWriteOptions.LIGHTS_DISABLE
            :param horn: horn
            :type horn: boolean, expected values : MachineWrite.MachineWriteOptions.HORN_ENABLE or MachineWrite.MachineWriteOptions.HORN_DISABLE
            :param auto_dig: auto dig function
            :type auto_dig: boolean, expected values MachineWrite.MachineWriteOptions.AUTO_DIG_ENABLE or MachineWrite.MachineWriteOptions.AUTO_DIG_DISABLE
            :param kick_down: kickdown for auto dig function
            :type kick_down: boolean, expected value : MachineWrite.MachineWriteOptions.KICK_DOWN_ENABLE or MachineWrite.MachineWriteOptions.KICK_DOWN_DISABLE
            """

            if (parking_brake == True) or (parking_brake == False):
                self.parking_brake = parking_brake
            else:
                logger.error('unknown value for parking_brake {} -> using PARKING_BRAKE_ENABLE instead'.format(parking_brake))
                self.parking_brake = MachineWrite.MachineWriteOptions.PARKING_BRAKE_ENABLE
            
            if (ecss_active == True) or (ecss_active == False):
                self.ecss_active = ecss_active
            else:
                logger.error('unknown value for ecss {} -> using ECSS_DISABLE instead'.format(ecss_active))
                self.ecss_active = MachineWrite.MachineWriteOptions.ECSS_DISABLE
            
            if (shift_hold_switch == True) or (shift_hold_switch == False):
                self.shift_hold_switch = shift_hold_switch
            else:
                logger.error('unknown value for shifthold {} -> using SHIFT_HOLD_DISABLE instead'.format(shift_hold_switch))
                self.shift_hold_switch=  MachineWrite.MachineWriteOptions.SHIFT_HOLD_SWITCH_DISABLE

            if (tm_cutoff == True) or (tm_cutoff == False):
                self.tm_cutoff = tm_cutoff
            else:
                logger.error('unknown value for tm_cutoff {} -> using TM_CUTOFF_DISABLE instead'.format(tm_cutoff))
                self.tm_cutoff = MachineWrite.MachineWriteOptions.TM_CUTOFF_DISABLE

            if (lights == True) or (lights == False):
                self.lights = lights
            else:
                logger.error('unknown value for lights {} -> using LIGHTS_DISABLE instead'.format(lights))
                self.lights = MachineWrite.MachineWriteOptions.LIGHTS_DISABLE
            
            if (horn == True) or (horn == False):
                self.horn = horn
            else:
                logger.error('unknown value for horn {} -> using HORN_DISABLE instead'.format(horn))
                self.horn = MachineWrite.MachineWriteOptions.HORN_DISABLE

            if (auto_dig == True) or (auto_dig == False):
                self.auto_dig = auto_dig
            else:
                logger.error('unknown value for autodig {} -> using AUTODIG_DISABLE instead'.format(auto_dig))
                self.auto_dig = MachineWrite.MachineWriteOptions.AUTO_DIG_DISABLE
            
            if (kick_down == True) or (kick_down == False):
                self.kick_down = kick_down
            else:
                logger.error('unkown value for kickdown {} -> using KICKDOWN_DISABLE instead'.format(kick_down))
                self.kick_down = MachineWrite.MachineWriteOptions.KICK_DOWN_DISABLE

        def __str__(self):
            return '\n\tparking_brake -> {}\n\tecss_active -> {}\n\tshift_hold_switch -> {}\n\ttm_cutoff -> {}\n\tlights -> {} \
            \n\thorn -> {}\n\tauto_dig -> {}\n\tkick_down ->{}\n'.format(
                self.parking_brake, 
                self.ecss_active, 
                self.shift_hold_switch, 
                self.tm_cutoff, 
                self.lights,
                self.horn, 
                self.auto_dig, 
                self.kick_down
            )


    def __init__(self, gear_speed, shift_mode, directional_sel, options, throttle, brake, boom, bucket, steering, ppc, disable_front_lidar=False):
        """
        __init__ Create a MachineWrite object, used to send commands to the... machine

        :param gear_speed: gear to engage
        :type gear_speed: int, expected values : MachineWrite.GS_1ST, MachineWrite.GS_2ND, MachineWrite.GS_3RD, MachineWrite.GS_4TH
        :param shift_mode: type of shifting mode
        :type shift_mode: int, expected values : MachineWrite.SM_MANUAL, MachineWrite.SM_LOW, MachineWrite.SM_HIGH
        :param directional_sel: direction of the machine
        :type directional_sel: int, expected values, MachineWrite.DM_NEUTRAL, MachineWrite.DM_REVERSE, MachineWrite.DM_FORWARD
        :param options: options such as lights, horn, etc.
        :type options: MachineWriteOptions
        :param throttle: throttle intensity for the main engine 
        :type throttle: float, expected values : [0..1.0] = [0..100.0%]
        :param brake: brake intensity 
        :type brake: float, expected values : [0..1.0] = [0..100.0%]
        :param boom: boom intensity 
        :type boom: float, expected values : [-1.0..1.0] = [-100.0%..100.0%]
        :param bucket: bucket intensity 
        :type bucket: float, expected values : [-1.0..1.0] = [-100.0%..100.0%]
        :param steering: steering intensity 
        :type steering: float, expected values : [-1.0..1.0] = [-100.0%..100.0%]
        :param ppc: ppc for shovel lock and release
        :type ppc: boolean, expected value : MachineWrite.PPC_LOCK_RELEASE_ENABLE or MachineWrite.PPC_LOCK_RELEASE_DISABLE
        :param disable_front_lidar: disable front lidar
        :type disable_front_lidar: boolean, expected value : MachineWrite.FRONT_LIDAR_DISABLE or MachineWrite.FRONT_LIDAR_ENABLE
        """
        if (gear_speed == MachineWrite.GS_1ST) or (gear_speed == MachineWrite.GS_2ND) or \
            (gear_speed == MachineWrite.GS_3RD) or (gear_speed == MachineWrite.GS_4TH):
            self.gear_speed = gear_speed
        else:
            logger.error('unknown gear speed {} -> using GS_1ST instead'.format(gear_speed))
            self.gear_speed = MachineWrite.GS_4TH

        if (shift_mode == MachineWrite.SM_LOW) or (shift_mode == MachineWrite.SM_HIGH) or \
            (shift_mode == MachineWrite.SM_MANUAL):
            self.shift_mode = shift_mode
        else:
            logger.error('unknown shiftmode {} -> using SM_LOW instead'.format(shift_mode))
            self.shift_mode = MachineWrite.SM_LOW

        if (directional_sel == MachineWrite.DM_FORWARD) or (directional_sel == MachineWrite.DM_NEUTRAL) or \
            (directional_sel == MachineWrite.DM_REVERSE):
            self.directional_sel = directional_sel
        else:
            logger.error('unknown directional mode {} -> using DM_NEUTRAL instead'.format(directional_sel))
            self.directional_sel = MachineWrite.DM_NEUTRAL

        self.options = options

        if (throttle >= 0.0) and (throttle <= 1.0):
            self.throttle = throttle
        else:
            logger.error('throttle out of range {} -> using 0.0 instead'.format(throttle))
            self.throttle = 0.0
    
        if (brake >= 0.0) and (brake <= 1.0):
            self.brake = brake
        else:
            logger.error('brake out of range {} -> using MachineWrite.DEFAULT_BRAKE instead'.format(brake))
            self.brake = MachineWrite.DEFAULT_BRAKE
        
        if (boom >= -1.0) and (boom <= 1.0):
            self.boom = boom
        else:
            logger.error('boom out of range {} -> using 0.0 instead'.format(boom))
            self.boom = 0.0
        
        if (bucket >= -1.0) and (bucket <= 1.0):
            self.bucket = bucket
        else:
            logger.error('bucket out of range {} -> using 0.0 instead'.format(bucket))
            self.bucket = 0.0

        if (steering >= -1.0) and (steering <= 1.0):
            self.steering = steering
        else:
            logger.error('steering out of range {} -> using 0.0 instead'.format(steering))
            self.steering = 0.0

        if (ppc == True) or (ppc == False):
            self.ppc = ppc
        else:
            logger.error('unkown value for ppc {} -> using PPC_LOCK_RELEASE_DISABLE instead'.format(ppc))
            self.ppc = MachineWrite.PPC_LOCK_RELEASE_DISABLE

        if (disable_front_lidar == True) or (disable_front_lidar == False):
            self.disable_front_lidar = disable_front_lidar
        else:
            logger.error('unkown value for disable_front_lidar {} -> using FRONT_LIDAR_ENABLE instead'.format(disable_front_lidar))
            self.disable_front_lidar = MachineWrite.FRONT_LIDAR_ENABLE

    @staticmethod
    def check_mv(gear_speed, shift_mode, directional_sel, options, throttle, brake, boom, bucket, steering, ppc, disable_front_lidar=False):
        """
        check_mv Create a MachineWrite object, same as constructor, but returns an error if one parameter is out of range

        :param gear_speed: gear to engage
        :type gear_speed: int, expected values : MachineWrite.GS_1ST, MachineWrite.GS_2ND, MachineWrite.GS_3RD, MachineWrite.GS_4TH
        :param shift_mode: type of shifting mode
        :type shift_mode: int, expected values : MachineWrite.SM_MANUAL, MachineWrite.SM_LOW, MachineWrite.SM_HIGH
        :param directional_sel: direction of the machine
        :type directional_sel: int, expected values, MachineWrite.DM_NEUTRAL, MachineWrite.DM_REVERSE, MachineWrite.DM_FORWARD
        :param options: options such as lights, horn, etc.
        :type options: MachineWriteOptions
        :param throttle: throttle intensity for the main engine 
        :type throttle: float, expected values : [0..1.0] = [0..100.0%]
        :param brake: brake intensity 
        :type brake: float, expected values : [0..1.0] = [0..100.0%]
        :param boom: boom intensity 
        :type boom: float, expected values : [-1.0..1.0] = [-100.0%..100.0%]
        :param bucket: bucket intensity 
        :type bucket: float, expected values : [-1.0..1.0] = [-100.0%..100.0%]
        :param steering: steering intensity 
        :type steering: float, expected values : [-1.0..1.0] = [-100.0%..100.0%]
        :param ppc: ppc for shovel lock and release
        :type ppc: boolean, expected value : MachineWrite.PPC_LOCK_RELEASE_ENABLE or MachineWrite.PPC_LOCK_RELEASE_DISABLE
        :param disable_front_lidar: disable front lidar
        :type disable_front_lidar: boolean, expected value : MachineWrite.FRONT_LIDAR_DISABLE or MachineWrite.FRONT_LIDAR_ENABLE
        :return: Tuple with error code and MachineWrite object
        :rtype: (Boolean, MachineWrite)
        """
        mv = MachineWrite(gear_speed, shift_mode, directional_sel, options, throttle, brake, boom, bucket, steering, ppc, disable_front_lidar)
        retcode = True

        if not ((gear_speed == MachineWrite.GS_1ST) or (gear_speed == MachineWrite.GS_2ND) or \
            (gear_speed == MachineWrite.GS_3RD) or (gear_speed == MachineWrite.GS_4TH)):
            mv.gear_speed = MachineWrite.GS_1ST
            retcode = False

        if not ((shift_mode == MachineWrite.SM_LOW) or (shift_mode == MachineWrite.SM_HIGH) or \
            (shift_mode == MachineWrite.SM_MANUAL)):
            mv.shift_mode = MachineWrite.SM_LOW
            retcode = False

        if not ((directional_sel == MachineWrite.DM_FORWARD) or (directional_sel == MachineWrite.DM_NEUTRAL) or \
            (directional_sel == MachineWrite.DM_REVERSE)):
            mv.directional_sel = MachineWrite.DM_NEUTRAL
            retcode = False

        if not ((throttle >= 0.0) and (throttle <= 1.0)):
            mv.throttle = 0.0
            retcode = False

        if not ((brake >= 0.0) and (brake <= 1.0)):
            mv.brake = MachineWrite.DEFAULT_BRAKE
            retcode = False

        if not ((boom >= -1.0) and (boom <= 1.0)):
            mv.boom = 0.0
            retcode = False
        
        if not ((bucket >= -1.0) and (bucket <= 1.0)):
            mv.bucket = 0.0
            retcode = False

        if not ((steering >= -1.0) and (steering <= 1.0)):
            mv.steering = 0.0
            retcode = False

        if not ((ppc == True) or (ppc == False)):
            mv.ppc = MachineWrite.PPC_LOCK_RELEASE_DISABLE
            retcode = False

        if not ((disable_front_lidar == True) or (disable_front_lidar == False)):
            mv.disable_front_lidar = MachineWrite.FRONT_LIDAR_ENABLE
            retcode = False

        return (retcode, mv)

    def __str__(self):
        return 'gear_speed -> {}\nshift_mode -> {}\ndirectional_sel -> {}\noptions -> {}\nthrottle -> {} \
            \nbrake -> {}\nboom -> {}\nbucket -> {}\nsteering -> {}\n\tppc ->{}\n\tdisable_front_lidar ->{}\n'.format(
                self.gear_speed, 
                self.shift_mode, 
                self.directional_sel, 
                self.options, 
                self.throttle, 
                self.brake, 
                self.boom,
                self.bucket, 
                self.steering,
                self.ppc,
                self.disable_front_lidar
        )

    
"""

    Tests

"""

if __name__ == '__main__':
   
    """
    ### TEST 0
    # test the constructor MachineWriteOptions

    # this one is good 
    mo = MachineWrite.MachineWriteOptions(
    MachineWrite.MachineWriteOptions.PARKING_BRAKE_DISABLE,
    MachineWrite.MachineWriteOptions.ECSS_DISABLE,
    MachineWrite.MachineWriteOptions.SHIFT_HOLD_SWITCH_DISABLE,
    MachineWrite.MachineWriteOptions.TM_CUTOFF_DISABLE,
    MachineWrite.MachineWriteOptions.LIGHTS_DISABLE,
    MachineWrite.MachineWriteOptions.HORN_DISABLE,
    MachineWrite.MachineWriteOptions.AUTO_DIG_DISABLE,
    MachineWrite.MachineWriteOptions.KICK_DOWN_DISABLE
    )
    print(mo)

    # another good one
    mo = MachineWrite.MachineWriteOptions(
    MachineWrite.MachineWriteOptions.PARKING_BRAKE_ENABLE,
    MachineWrite.MachineWriteOptions.ECSS_ENABLE,
    MachineWrite.MachineWriteOptions.SHIFT_HOLD_SWITCH_ENABLE,
    MachineWrite.MachineWriteOptions.TM_CUTOFF_ENABLE,
    MachineWrite.MachineWriteOptions.LIGHTS_ENABLE,
    MachineWrite.MachineWriteOptions.HORN_ENABLE,
    MachineWrite.MachineWriteOptions.AUTO_DIG_ENABLE,
    MachineWrite.MachineWriteOptions.KICK_DOWN_ENABLE
    )
    print(mo)

    # bad one
    mo = MachineWrite.MachineWriteOptions(
    3, 3, 3, 3, 3, 3, 3, 3
    )
    print(mo)
    """

    """
    ### TEST 1
    # test the constructor MachineWrite
    
    # options are already check 
    mo = MachineWrite.MachineWriteOptions(
        MachineWrite.MachineWriteOptions.PARKING_BRAKE_DISABLE,
        MachineWrite.MachineWriteOptions.ECSS_DISABLE,
        MachineWrite.MachineWriteOptions.SHIFT_HOLD_SWITCH_DISABLE,
        MachineWrite.MachineWriteOptions.TM_CUTOFF_DISABLE,
        MachineWrite.MachineWriteOptions.LIGHTS_DISABLE,
        MachineWrite.MachineWriteOptions.HORN_DISABLE,
        MachineWrite.MachineWriteOptions.AUTO_DIG_DISABLE,
        MachineWrite.MachineWriteOptions.KICK_DOWN_DISABLE
    )

    # good one
    mw = MachineWrite(
        MachineWrite.GS_1ST,
        MachineWrite.SM_MANUAL,
        MachineWrite.DM_NEUTRAL,
        mo, 
        0.0, 
        0.0,
        -1.0,
        -1.0,
        -1.0,
        MachineWrite.PPC_LOCK_RELEASE_ENABLE,
        MachineWrite.FRONT_LIDAR_DISABLE
    )
    print(mw)

    # good one
    mw = MachineWrite(
        MachineWrite.GS_2ND,
        MachineWrite.SM_LOW,
        MachineWrite.DM_FORWARD,
        mo, 
        1.0, 
        1.0,
        1.0,
        1.0,
        1.0,
        MachineWrite.PPC_LOCK_RELEASE_DISABLE,
        MachineWrite.FRONT_LIDAR_ENABLE
    )
    print(mw)

    # good one
    mw = MachineWrite(
        MachineWrite.GS_3RD,
        MachineWrite.SM_HIGH,
        MachineWrite.DM_REVERSE,
        mo, 
        1.0, 
        1.0,
        1.0,
        1.0,
        1.0,
        MachineWrite.PPC_LOCK_RELEASE_DISABLE,
        MachineWrite.FRONT_LIDAR_ENABLE
    )
    print(mw)

    # good one
    mw = MachineWrite(
        MachineWrite.GS_4TH,
        MachineWrite.SM_LOW,
        MachineWrite.DM_FORWARD,
        mo, 
        1.0, 
        1.0,
        1.0,
        1.0,
        1.0,
        MachineWrite.PPC_LOCK_RELEASE_DISABLE,
        MachineWrite.FRONT_LIDAR_ENABLE
    )
    print(mw)

    # bad one
    mw = MachineWrite(
        5, 
        5, 
        5,
        mo, 
        1.1, 
        1.1,
        1.1,
        1.1,
        1.1,
        2,
        3
    )
    print(mw)

    # bad one
    mw = MachineWrite(
        5, 
        5, 
        5,
        mo, 
        -0.1, 
        -0.1,
        -1.1,
        -1.1,
        -1.1,
        MachineWrite.PPC_LOCK_RELEASE_DISABLE,
        MachineWrite.FRONT_LIDAR_ENABLE
    )
    print(mw)

    # options are already check 
    mo = MachineWrite.MachineWriteOptions(
        MachineWrite.MachineWriteOptions.PARKING_BRAKE_DISABLE,
        MachineWrite.MachineWriteOptions.ECSS_DISABLE,
        MachineWrite.MachineWriteOptions.SHIFT_HOLD_SWITCH_DISABLE,
        MachineWrite.MachineWriteOptions.TM_CUTOFF_DISABLE,
        MachineWrite.MachineWriteOptions.LIGHTS_DISABLE,
        MachineWrite.MachineWriteOptions.HORN_DISABLE,
        MachineWrite.MachineWriteOptions.AUTO_DIG_DISABLE,
        MachineWrite.MachineWriteOptions.KICK_DOWN_DISABLE
    )

    # good one
    mw = MachineWrite(
        MachineWrite.GS_1ST,
        MachineWrite.SM_MANUAL,
        MachineWrite.DM_NEUTRAL,
        mo, 
        0.0, 
        0.0,
        -1.0,
        -1.0,
        -1.0,
        MachineWrite.PPC_LOCK_RELEASE_ENABLE
    )
    print(mw)
    """



    ##############################################
    # test static method
    ##############################################

    mo = MachineWrite.MachineWriteOptions(
        MachineWrite.MachineWriteOptions.PARKING_BRAKE_DISABLE,
        MachineWrite.MachineWriteOptions.ECSS_DISABLE,
        MachineWrite.MachineWriteOptions.SHIFT_HOLD_SWITCH_DISABLE,
        MachineWrite.MachineWriteOptions.TM_CUTOFF_DISABLE,
        MachineWrite.MachineWriteOptions.LIGHTS_DISABLE,
        MachineWrite.MachineWriteOptions.HORN_DISABLE,
        MachineWrite.MachineWriteOptions.AUTO_DIG_DISABLE,
        MachineWrite.MachineWriteOptions.KICK_DOWN_DISABLE
    )

    # should be good
    retcode, mv = MachineWrite.check_mv(
        MachineWrite.GS_1ST,
        MachineWrite.SM_MANUAL,
        MachineWrite.DM_NEUTRAL,
        mo, 
        0.0, 
        0.0,
        -1.0,
        -1.0,
        -1.0,
        MachineWrite.PPC_LOCK_RELEASE_ENABLE,
        MachineWrite.FRONT_LIDAR_DISABLE
    )
    if retcode:
        logger.success('Test valid')
        logger.info(mv)
    else:
        logger.error('failed test')
        logger.info(mv)

    # should fail
    retcode, mv = MachineWrite.check_mv(
        -1,
        MachineWrite.SM_MANUAL,
        MachineWrite.DM_NEUTRAL,
        mo, 
        0.0, 
        0.0,
        -1.0,
        -1.0,
        -1.0,
        MachineWrite.PPC_LOCK_RELEASE_ENABLE,
        MachineWrite.FRONT_LIDAR_DISABLE
    )
    if retcode:
        logger.success('Test valid')
        logger.info(mv)
    else:
        logger.error('failed test')
        logger.info(mv)

    # should fail
    retcode, mv = MachineWrite.check_mv(
        MachineWrite.GS_1ST,
        -1,
        MachineWrite.DM_NEUTRAL,
        mo, 
        0.0, 
        0.0,
        -1.0,
        -1.0,
        -1.0,
        MachineWrite.PPC_LOCK_RELEASE_ENABLE,
        MachineWrite.FRONT_LIDAR_DISABLE
    )
    if retcode:
        logger.success('Test valid')
        logger.info(mv)
    else:
        logger.error('failed test')
        logger.info(mv)

    # should fail
    retcode, mv = MachineWrite.check_mv(
        MachineWrite.GS_1ST,
        MachineWrite.SM_MANUAL,
        -1,
        mo, 
        0.0, 
        0.0,
        -1.0,
        -1.0,
        -1.0,
        MachineWrite.PPC_LOCK_RELEASE_ENABLE,
        MachineWrite.FRONT_LIDAR_DISABLE
    )
    if retcode:
        logger.success('Test valid')
        logger.info(mv)
    else:
        logger.error('failed test')
        logger.info(mv)

    # should fail
    retcode, mv = MachineWrite.check_mv(
        MachineWrite.GS_1ST,
        MachineWrite.SM_MANUAL,
        MachineWrite.DM_NEUTRAL,
        mo, 
        -1.0, 
        0.0,
        -1.0,
        -1.0,
        -1.0,
        MachineWrite.PPC_LOCK_RELEASE_ENABLE,
        MachineWrite.FRONT_LIDAR_DISABLE
    )
    if retcode:
        logger.success('Test valid')
        logger.info(mv)
    else:
        logger.error('failed test')
        logger.info(mv)

    # should fail
    retcode, mv = MachineWrite.check_mv(
        MachineWrite.GS_1ST,
        MachineWrite.SM_MANUAL,
        MachineWrite.DM_NEUTRAL,
        mo, 
        0.0, 
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        MachineWrite.PPC_LOCK_RELEASE_ENABLE,
        MachineWrite.FRONT_LIDAR_DISABLE
    )
    if retcode:
        logger.success('Test valid')
        logger.info(mv)
    else:
        logger.error('failed test')
        logger.info(mv)

    # should fail
    retcode, mv = MachineWrite.check_mv(
        MachineWrite.GS_1ST,
        MachineWrite.SM_MANUAL,
        MachineWrite.DM_NEUTRAL,
        mo, 
        0.0, 
        0.0,
        2.0,
        -1.0,
        -1.0,
        MachineWrite.PPC_LOCK_RELEASE_ENABLE,
        MachineWrite.FRONT_LIDAR_DISABLE
    )
    if retcode:
        logger.success('Test valid')
        logger.info(mv)
    else:
        logger.error('failed test')
        logger.info(mv)

    # should fail
    retcode, mv = MachineWrite.check_mv(
        MachineWrite.GS_1ST,
        MachineWrite.SM_MANUAL,
        MachineWrite.DM_NEUTRAL,
        mo, 
        0.0, 
        0.0,
        -1.0,
        2.0,
        -1.0,
        MachineWrite.PPC_LOCK_RELEASE_ENABLE,
        MachineWrite.FRONT_LIDAR_DISABLE
    )
    if retcode:
        logger.success('Test valid')
        logger.info(mv)
    else:
        logger.error('failed test')
        logger.info(mv)

    # should fail
    retcode, mv = MachineWrite.check_mv(
        MachineWrite.GS_1ST,
        MachineWrite.SM_MANUAL,
        MachineWrite.DM_NEUTRAL,
        mo, 
        0.0, 
        0.0,
        -1.0,
        -1.0,
        2.0,
        MachineWrite.PPC_LOCK_RELEASE_ENABLE,
        MachineWrite.FRONT_LIDAR_DISABLE
    )
    if retcode:
        logger.success('Test valid')
        logger.info(mv)
    else:
        logger.error('failed test')
        logger.info(mv)

    # should fail
    retcode, mv = MachineWrite.check_mv(
        MachineWrite.GS_1ST,
        MachineWrite.SM_MANUAL,
        MachineWrite.DM_NEUTRAL,
        mo, 
        0.0, 
        0.0,
        -1.0,
        -1.0,
        -1.0,
        -1,
        MachineWrite.FRONT_LIDAR_DISABLE
    )
    if retcode:
        logger.success('Test valid')
        logger.info(mv)
    else:
        logger.error('failed test')
        logger.info(mv)

    # should fail
    retcode, mv = MachineWrite.check_mv(
        MachineWrite.GS_1ST,
        MachineWrite.SM_MANUAL,
        MachineWrite.DM_NEUTRAL,
        mo,
        0.0, 
        0.0,
        -1.0,
        -1.0,
        -1.0,
        MachineWrite.PPC_LOCK_RELEASE_ENABLE,
        -1
    )
    if retcode:
        logger.success('Test valid')
        logger.info(mv)
    else:
        logger.error('failed test')
        logger.info(mv)