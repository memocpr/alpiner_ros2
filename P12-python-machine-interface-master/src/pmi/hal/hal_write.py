from loguru import logger

from pmi.machine.machine_to_hal.machine_write import MachineWrite


class HAL_Write:

    """
    constants to be used in HAL world,
    with the Modbus registers.
    for all other usage, check the class MachineWrite.
    """
    GS_1ST = 0x0001
    GS_2ND = 0x0002
    GS_3RD = 0x0004
    GS_4TH = 0x0008
    SM_LOW = 0x0000
    SM_MANUAL = 0x0100
    SM_HIGH = 0x0200
    DM_NEUTRAL = 0x0001
    DM_REVERSE = 0x0002
    DM_FORWARD = 0x0004
    PPC_LOCK_RELEASE_ENABLE = 0x0008
    PPC_LOCK_RELEASE_DISABLE = 0x0000
    FRONT_LIDAR_DISABLE = 0x0010
    FRONT_LIDAR_ENABLE = 0x0000

    # conversion dicts, from Machine's world to HAL world
    GEAR_SPEED = {
        MachineWrite.GS_1ST : GS_1ST,
        MachineWrite.GS_2ND : GS_2ND,
        MachineWrite.GS_3RD : GS_3RD,
        MachineWrite.GS_4TH : GS_4TH,
    }

    SHIFTMODE = {
        MachineWrite.SM_LOW : SM_LOW,
        MachineWrite.SM_HIGH : SM_HIGH,
        MachineWrite.SM_MANUAL : SM_MANUAL
    }

    DIR_MODE = {
        MachineWrite.DM_FORWARD : DM_FORWARD,
        MachineWrite.DM_REVERSE : DM_REVERSE,
        MachineWrite.DM_NEUTRAL : DM_NEUTRAL
    }

    PPC_LOCK_RELEASE = {
        MachineWrite.PPC_LOCK_RELEASE_ENABLE : PPC_LOCK_RELEASE_ENABLE,
        MachineWrite.PPC_LOCK_RELEASE_DISABLE : PPC_LOCK_RELEASE_DISABLE
    }

    FRONT_LIDAR = {
        MachineWrite.FRONT_LIDAR_DISABLE : FRONT_LIDAR_DISABLE,
        MachineWrite.FRONT_LIDAR_ENABLE : FRONT_LIDAR_ENABLE
    }

    # options
    class HAL_WriteOptions:

        """
        constants to be used in HAL world,
        with the Modbus registers.
        for all other usage, check the class MachineWrite.
        """
        PARKING_BRAKE_ENABLE = 0x00  # /!\ inversion
        PARKING_BRAKE_DISABLE = 0x01 # /!\ inversion
        ECSS_ENABLE = 0x02
        ECSS_DISABLE = 0x00
        SHIFT_HOLD_SWITCH_ENABLE = 0x04
        SHIFT_HOLD_SWITCH_DISABLE = 0x00
        TM_CUTOFF_ENABLE = 0x08
        TM_CUTOFF_DISABLE = 0x00
        LIGHTS_ENABLE = 0x10
        LIGHTS_DISABLE = 0x00
        HORN_ENABLE = 0x20
        HORN_DISABLE = 0x00
        AUTO_DIG_ENABLE = 0x40
        AUTO_DIG_DISABLE = 0x00
        KICK_DOWN_ENABLE = 0x80
        KICK_DOWN_DISABLE = 0x00

        # conversion dicts, from Machine's world to HAL world
        PARKING_BRAKE = {
            MachineWrite.MachineWriteOptions.PARKING_BRAKE_DISABLE : PARKING_BRAKE_DISABLE,
            MachineWrite.MachineWriteOptions.PARKING_BRAKE_ENABLE : PARKING_BRAKE_ENABLE
        }

        ECSS = {
            MachineWrite.MachineWriteOptions.ECSS_ENABLE : ECSS_ENABLE,
            MachineWrite.MachineWriteOptions.ECSS_DISABLE : ECSS_DISABLE
        }

        SHIFT_HOLD_SWITCH = {
            MachineWrite.MachineWriteOptions.SHIFT_HOLD_SWITCH_DISABLE : SHIFT_HOLD_SWITCH_DISABLE,
            MachineWrite.MachineWriteOptions.SHIFT_HOLD_SWITCH_ENABLE : SHIFT_HOLD_SWITCH_ENABLE
        }

        TM_CUTOFF = {
            MachineWrite.MachineWriteOptions.TM_CUTOFF_DISABLE : TM_CUTOFF_DISABLE,
            MachineWrite.MachineWriteOptions.TM_CUTOFF_ENABLE : TM_CUTOFF_ENABLE
        }

        LIGHTS = {
            MachineWrite.MachineWriteOptions.LIGHTS_DISABLE : LIGHTS_DISABLE,
            MachineWrite.MachineWriteOptions.LIGHTS_ENABLE : LIGHTS_ENABLE
        }

        HORN = {
            MachineWrite.MachineWriteOptions.HORN_DISABLE : HORN_DISABLE,
            MachineWrite.MachineWriteOptions.HORN_ENABLE : HORN_ENABLE
        }

        AUTODIG = {
            MachineWrite.MachineWriteOptions.AUTO_DIG_DISABLE : AUTO_DIG_DISABLE,
            MachineWrite.MachineWriteOptions.AUTO_DIG_ENABLE : AUTO_DIG_ENABLE
        }

        KICKDOWN = {
            MachineWrite.MachineWriteOptions.KICK_DOWN_DISABLE : KICK_DOWN_DISABLE,
            MachineWrite.MachineWriteOptions.KICK_DOWN_ENABLE : KICK_DOWN_ENABLE
        }
        
        def __init__(self, parking_brake, ecss_active, shift_hold_switch, tm_cutoff, lights, horn, auto_dig, kick_down):
            """
            __init__ Create an object that represents the write options, encoded in the register 1's MSB

            :param parking_brake: enable/disable parking brake, 0 being activated, 1 being disabled
            :type parking_brake: uint8, expected value : HAL_Write.HAL_WriteOptions.PARKING_BRAKE_ENABLE or HAL_Write.HAL_WriteOptions.PARKING_BRAKE_DISABLE
            :param ecss_active: enable/disable ECSS (Electronic Control Suspension System)
            :type ecss_active: uint8, expected value : HAL_Write.HAL_WriteOptions.ECSS_ENABLE or HAL_Write.HAL_WriteOptions.ECSS_DISABLE
            :param shift_hold_switch: block automatically upshifts 
            :type shift_hold_switch: uint8, expected value HAL_Write.HAL_WriteOptions.SHIFT_HOLD_SWITCH_ENABLE or HAL_Write.HAL_WriteOptions.SHIFT_HOLD_SWITCH_DISABLE
            :param tm_cutoff: shift gear to Neutral with parking brake
            :type tm_cutoff: uint8, expected value : HAL_Write.HAL_WriteOptions.TM_CUTOFF_ENABLE or HAL_Write.HAL_WriteOptions.TM_CUTOFF_DISABLE
            :param lights: lights
            :type lights: uint8, expected value : HAL_Write.HAL_WriteOptions.LIGHTS_ENABLE or HAL_Write.HAL_WriteOptions.LIGHTS_DISABLE
            :param horn: horn
            :type horn: uint8, expected values : HAL_Write.HAL_WriteOptions.HORN_ENABLE or HAL_Write.HAL_WriteOptions.HORN_DISABLE
            :param auto_dig: auto dig function
            :type auto_dig: uint8, expected values HAL_Write.HAL_WriteOptions.AUTO_DIG_ENABLE or HAL_Write.HAL_WriteOptions.AUTO_DIG_DISABLE
            :param kick_down: kickdown for auto dig function
            :type kick_down: uint8, expected value : HAL_Write.HAL_WriteOptions.KICK_DOWN_ENABLE or HAL_Write.HAL_WriteOptions.KICK_DOWN_DISABLE
            """
            if (parking_brake == HAL_Write.HAL_WriteOptions.PARKING_BRAKE_ENABLE) or (parking_brake == HAL_Write.HAL_WriteOptions.PARKING_BRAKE_DISABLE):
                self.parking_brake = parking_brake
            else:
                logger.error('Parking brake is unknown {} -> using PARKING_BRAKE_ENABLE instead'.format(parking_brake))
                self.parking_brake = HAL_Write.HAL_WriteOptions.PARKING_BRAKE_ENABLE

            if (ecss_active == HAL_Write.HAL_WriteOptions.ECSS_ENABLE) or (ecss_active == HAL_Write.HAL_WriteOptions.ECSS_DISABLE):
                self.ecss_active = ecss_active
            else:
                logger.error('ECSS is unknown {} -> using ECSS_DISABLE instead'.format(ecss_active))
                self.ecss_active = HAL_Write.HAL_WriteOptions.ECSS_DISABLE

            if (shift_hold_switch == HAL_Write.HAL_WriteOptions.SHIFT_HOLD_SWITCH_ENABLE) or (shift_hold_switch == HAL_Write.HAL_WriteOptions.SHIFT_HOLD_SWITCH_DISABLE):
               self.shift_hold_switch = shift_hold_switch
            else:
                logger.error('Shift hold is unkown {} -> using SHIFT_HOLD_SWITCH_DISABLE instead'.format(shift_hold_switch))
                self.shift_hold_switch = HAL_Write.HAL_WriteOptions.SHIFT_HOLD_SWITCH_DISABLE

            if (tm_cutoff == HAL_Write.HAL_WriteOptions.TM_CUTOFF_ENABLE) or (tm_cutoff == HAL_Write.HAL_WriteOptions.TM_CUTOFF_DISABLE):
                self.tm_cutoff = tm_cutoff
            else:
                logger.error('tm cutoff is unknown {} -> using TM_CUTOFFF_DISABLE instead'.format(tm_cutoff))
                self.tm_cutoff = HAL_Write.HAL_WriteOptions.TM_CUTOFF_DISABLE
            
            if (lights == HAL_Write.HAL_WriteOptions.LIGHTS_ENABLE) or (lights == HAL_Write.HAL_WriteOptions.LIGHTS_DISABLE):
                self.lights = lights
            else:
                logger.error('Lights is unknown {} -> using LIGHTS_DISABLE instead'.format(lights))
                self.lights = HAL_Write.HAL_WriteOptions.LIGHTS_DISABLE

            if (horn == HAL_Write.HAL_WriteOptions.HORN_ENABLE) or (horn == HAL_Write.HAL_WriteOptions.HORN_DISABLE):
                self.horn = horn
            else:
                logger.error('Horn is unknown {} : using HORN_DISABLE instead'.format(horn))
                self.horn = HAL_Write.HAL_WriteOptions.HORN_DISABLE

            if (auto_dig == HAL_Write.HAL_WriteOptions.AUTO_DIG_ENABLE) or (auto_dig == HAL_Write.HAL_WriteOptions.AUTO_DIG_DISABLE):
                self.auto_dig = auto_dig
            else:
                logger.error('Autodig is unknown {} -> using AUTODIG_DISABLE instead'.format(auto_dig))
                self.auto_dig = HAL_Write.HAL_WriteOptions.AUTO_DIG_DISABLE

            if (kick_down == HAL_Write.HAL_WriteOptions.KICK_DOWN_ENABLE) or (kick_down == HAL_Write.HAL_WriteOptions.KICK_DOWN_DISABLE):
                self.kick_down = kick_down
            else:
                logger.error('Kickdown is unknown {} -> using KICK_DOWN_DISABLE instead'.format(kick_down))
                self.kick_down = HAL_Write.HAL_WriteOptions.KICK_DOWN_DISABLE

        def __str__(self):
            return '\n\tparking_brake -> {}\n\tecss_active -> {}\n\tshift_hold_switch -> {}\n\ttm_cutoff -> {}\n\tlights -> {} \
            \n\thorn -> {}\n\tauto_dig -> {}\n\tkick_down -> {}\n'.format(
                self.parking_brake, 
                self.ecss_active, 
                self.shift_hold_switch, 
                self.tm_cutoff, 
                self.lights,
                self.horn, 
                self.auto_dig, 
                self.kick_down
            )

        def encode_options(self):
            """
            encode_options Encode the options into a Uint16 number (options are therefore already encoded in the MSB, no need for a further shift)

            :return: encoded options
            :rtype: Uint16
            """
            byte = (self.parking_brake & 0x01) \
                | (self.ecss_active & 0x02)\
                    | (self.shift_hold_switch & 0x04)\
                        | (self.tm_cutoff & 0x08)\
                            | (self.lights & 0x10)\
                                | (self.horn & 0x20)\
                                    | (self.auto_dig & 0x40)\
                                        | (self.kick_down & 0x80)
            return (byte & 0x00ff) << 8

        @staticmethod
        def import_from_machine_options(machine_options):
            """
            import_from_machine_options import values from a MachineWriteOptions object 

            :param machine_options: object to import from
            :type machine_options: MachineWriteOptions
            :return: HAL_WriteOptions object
            :rtype: HAL_WriteOptions
            """
            # conversions
            if machine_options.parking_brake in HAL_Write.HAL_WriteOptions.PARKING_BRAKE:
                parking_brake = HAL_Write.HAL_WriteOptions.PARKING_BRAKE[machine_options.parking_brake]
            else:
                logger.error('Conversion from MachineWriteOptions to HAL_WriteOptions failed due to bad input parking brake {} -> using PARKING_BRAKE_ENABLE instead.'.format(machine_options.parking_brake))
                parking_brake = HAL_Write.HAL_WriteOptions.PARKING_BRAKE_ENABLE

            if machine_options.ecss_active in HAL_Write.HAL_WriteOptions.ECSS:
                ecss_active = HAL_Write.HAL_WriteOptions.ECSS[machine_options.ecss_active]
            else:
                logger.error('Conversion from MachineWriteOptions to HAL_WriteOptions failed due to bad input ecss {} -> using ECSS_DISABLE instead.'.format(machine_options.ecss_active))
                ecss_active = HAL_Write.HAL_WriteOptions.ECSS_DISABLE

            if machine_options.shift_hold_switch in HAL_Write.HAL_WriteOptions.SHIFT_HOLD_SWITCH:
                shift_hold_switch = HAL_Write.HAL_WriteOptions.SHIFT_HOLD_SWITCH[machine_options.shift_hold_switch]
            else:
                logger.error('Conversion from MachineWriteOptions to HAL_WriteOptions failed due to bad input shift hold switch {} -> using SHIFT_HOLD_DISABLE instead.'.format(machine_options.shift_hold_switch))
                shift_hold_switch = HAL_Write.HAL_WriteOptions.SHIFT_HOLD_SWITCH_DISABLE

            if machine_options.tm_cutoff in HAL_Write.HAL_WriteOptions.TM_CUTOFF:
                tm_cutoff = HAL_Write.HAL_WriteOptions.TM_CUTOFF[machine_options.tm_cutoff]
            else:
                logger.error('Conversion from MachineWriteOptions to HAL_WriteOptions failed due to bad input tm_cutoff {} -> using TM_CUTOFF_DISABLE.'.format(machine_options.tm_cutoff))
                tm_cutoff = HAL_Write.HAL_WriteOptions.TM_CUTOFF_DISABLE

            if machine_options.lights in HAL_Write.HAL_WriteOptions.LIGHTS:
                lights = HAL_Write.HAL_WriteOptions.LIGHTS[machine_options.lights]
            else:
                logger.error('Conversion from MachineWriteOptions to HAL_WriteOptions failed due to bad input lights {} -> using LIGHTS_DISABLE instead.'.format(machine_options.lights))
                lights = HAL_Write.HAL_WriteOptions.LIGHTS_DISABLE

            if machine_options.horn in HAL_Write.HAL_WriteOptions.HORN:
                horn = HAL_Write.HAL_WriteOptions.HORN[machine_options.horn]
            else:
                logger.error('Conversion from MachineWriteOptions to HAL_WriteOptions failed due to bad input horn {} -> using HORN_DISABLE instead.'.format(machine_options.horn))
                horn = HAL_Write.HAL_WriteOptions.HORN_DISABLE

            if machine_options.auto_dig in HAL_Write.HAL_WriteOptions.AUTODIG:
                auto_dig = HAL_Write.HAL_WriteOptions.AUTODIG[machine_options.auto_dig]
            else:
                logger.error('Conversion from MachineWriteOptions to HAL_WriteOptions failed due to bad input autodig {} -> using AUTO_DIG_DISABLE instead.'.format(machine_options.auto_dig))
                auto_dig = HAL_Write.HAL_WriteOptions.AUTO_DIG_DISABLE  

            if machine_options.kick_down in HAL_Write.HAL_WriteOptions.KICKDOWN:
                kick_down = HAL_Write.HAL_WriteOptions.KICKDOWN[machine_options.kick_down]
            else:
                logger.error('Conversion from MachineWriteOptions to HAL_WriteOptions failed due to bad input kickdown {} -> using KICKDOWN_DISABLE instead.'.format(machine_options.kick_down))
                kick_down = HAL_Write.HAL_WriteOptions.KICK_DOWN_DISABLE

            return HAL_Write.HAL_WriteOptions(
                parking_brake, 
                ecss_active, 
                shift_hold_switch, 
                tm_cutoff,
                lights, 
                horn,
                auto_dig,
                kick_down
            )

    def __init__(self, gear_speed, shift_mode, directional_sel, options, throttle, brake, boom, bucket, steering, ppc, disable_front_lidar):
        """
        __init__ Create a HAL_Write object, used to send commands to the... machine

        :param gear_speed: gear to engage
        :type gear_speed: Uint16, expected values : HAL_Write.GS_1ST, HAL_Write.GS_2ND, HAL_Write.GS_3RD, HAL_Write.GS_4TH
        :param shift_mode: type of shifting mode
        :type shift_mode: Uint16, expected values : HAL_Write.SM_MANUAL, HAL_Write.SM_LOW, HAL_Write.SM_HIGH
        :param directional_sel: direction of the machine
        :type directional_sel: Uint16, expected values, HAL_Write.DM_NEUTRAL, HAL_Write.DM_REVERSE, HAL_Write.DM_FORWARD
        :param options: options such as lights, horn, etc.
        :type options: HAL_WriteOptions
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
        :param ppc: ppc state
        :type ppc: Uint8, expected values, HAL_WRITE.PPC_LOCK_RELEASE_ENABLE, HAL_WRITE.PPC_LOCK_RELEASE_DISABLE
        :param disable_front_lidar: disable front lidar state
        :type disable_front_lidar: Uint8, expected values, HAL_WRITE.FRONT_LIDAR_DISABLE, HAL_WRITE.FRONT_LIDAR_ENABLE
        """
        if ((gear_speed == HAL_Write.GS_1ST) or (gear_speed == HAL_Write.GS_2ND) or \
            (gear_speed == HAL_Write.GS_3RD) or (gear_speed == HAL_Write.GS_4TH)):
            self.gear_speed = gear_speed
        else:
            logger.error('Gear speed is not known {} -> taking GS_1ST instead ! '.format(gear_speed))
            self.gear_speed = HAL_Write.GS_4TH

        if (shift_mode == HAL_Write.SM_MANUAL) or (shift_mode == HAL_Write.SM_LOW) or \
            (shift_mode == HAL_Write.SM_HIGH):
            self.shift_mode = shift_mode
        else:
            logger.error('Shift mode is not known {} -> taking SM_LOW instead ! '.format(shift_mode))
            self.shift_mode = HAL_Write.SM_LOW

        if (directional_sel == HAL_Write.DM_NEUTRAL) or (directional_sel == HAL_Write.DM_FORWARD) or \
            (directional_sel == HAL_Write.DM_REVERSE):
            self.directional_sel = directional_sel
        else:
            logger.error('Directional mode is not known {} -> taking DM_NEUTRAL instead ! '.format(directional_sel))
            self.directional_sel = HAL_Write.DM_NEUTRAL

        # options are already safely checked in constructor
        self.options = options

        if (throttle >= 0.0) and (throttle <= 1.0):
            self.throttle = throttle
        else:
            logger.error('Throttle out of range {} -> using 0.0 instead'.format(throttle))
            self.throttle = 0.0

        if (brake >= 0.0) and (brake <= 1.0):
            self.brake = brake
        else:
            logger.error('Brake out of range {} -> using MachineWrite.DEFAULT_BRAKE instead'.format(brake))
            self.brake = MachineWrite.DEFAULT_BRAKE

        if (boom >= -1.0) and (boom <= 1.0):
            self.boom = boom
        else:
            logger.error('Boom out of range {} -> using 0.0 instead'.format(boom))
            self.boom = 0.0
        
        if (bucket >= -1.0) and (bucket <= 1.0):
            self.bucket = bucket
        else:
            logger.error('Bucket out of range {} -> using 0.0 instead'.format(bucket))
            self.bucket = 0.0

        if (steering >= -1.0) and (steering <= 1.0):
            self.steering = steering
        else:
            logger.error('Steering out of range {} -> using 0.0 instead'.format(steering))
            self.steering = 0.0

        if (ppc == HAL_Write.PPC_LOCK_RELEASE_ENABLE) or (ppc == HAL_Write.PPC_LOCK_RELEASE_DISABLE):
                self.ppc = ppc
        else:
            logger.error('ppc is unknown {} : using PPC_LOCK_RELEASE_DISABLE instead'.format(ppc))
            self.ppc = HAL_Write.PPC_LOCK_RELEASE_DISABLE

        if (disable_front_lidar == HAL_Write.FRONT_LIDAR_ENABLE) or (disable_front_lidar == HAL_Write.FRONT_LIDAR_DISABLE):
            self.disable_front_lidar = disable_front_lidar
        else:
            logger.error('disable_front_lidar is unknown {} : using FRONT_LIDAR_ENABLE instead'.format(disable_front_lidar))
            self.disable_front_lidar = HAL_Write.FRONT_LIDAR_ENABLE

    def __str__(self):
        return 'gear_speed -> {}\nshift_mode -> {}\ndirectional_sel -> {}\noptions -> {}\nthrottle -> {} \
            \nbrake -> {}\nboom -> {}\nbucket -> {}\nsteering -> {}\nppc -> {}\ndisable front lidar -> {}\n'.format(
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

    def convert_to_bytes(self):
        """
        convert_to_bytes Convert the HAL_Write object to a list of registers

        :return: List of registers
        :rtype: List
        """
        # register 0 contains : 
        #   LSB : gear speed    [res, res, res, res, 4th, 3rd, 2nd, 1st]
        #   MSB : shift mode    [res, res, res, res, res, res, active high, active manual] 
        register_0 = self.gear_speed + self.shift_mode # shift mode must already be shifted to left by 8 
        #logger.debug('register 0 : {}'.format(format(register_0, '#06x')))

        # register 1 contains :
        #   LSB : directional sel   [res, res, res, Disable front lidar, PPC Lock/Release, forward, reverse, neutral]
        #   MSB : options           [kick down, auto dig, horn, lights, t/M cutoff, shift hold, ESSC active, parking brake]
        ppc = self.ppc
        disable_front_lidar = self.disable_front_lidar
        directional_sel = self.directional_sel
        options = self.options.encode_options()
        register_1 = disable_front_lidar + ppc + directional_sel + options # options are already shifted to left by 8
        #logger.debug('register 1 : {}'.format(format(register_1, '#06x')))

        # register 2 contains : 
        #   LSB : throttle  [0..255] = [0..100%]
        #   MSB : brake     [0..255] = [0..100%]
        # convert from input range [0..1.0] to range [0..255]
        # but first make sure it is in the right range
        if (self.throttle < 0.0)  or (self.throttle > 1.0):
            logger.error('Throttle command is not in the input range, should be [0.0..1.0], but it is {}'.format(self.throttle))
            self.throttle = 0.0
        throttle = int(self.throttle * 255.0)
        # check brake range
        if self.brake < 0.0:
            logger.error('Brake command is not in the input range, should be [0.0..1.0], but it is {}'.format(self.brake))
            self.brake = 0.0
        if self.brake > 1.0:
            logger.error('Brake command is not in the input range, should be [0.0..1.0], but it is {}'.format(self.brake))
            self.brake = 1.0
        brake = int(self.brake * 255.0)
        register_2 = (throttle & 0x00ff) | ((brake & 0x00ff) << 8)
        #logger.debug('register 2 : {}'.format(format(register_2, '#06x')))

        # register 3 contains : 
        #   LSB : boom      [-128..127] = [-100.0%..100.0%]
        #   MSB : bucket    [-128..127] = [-100.0%..100.0%]
        # convert from input range [-1.0..1.0] to range [-128..127]
        if (self.bucket < -1.0) or (self.bucket > 1.0):
            logger.error('Bucket command is not in the input range, should be [-1.0..1.0], but it is {}'.format(self.bucket))
            self.bucket = 0.0
        bucket = HAL_Write.convert_percent_to_int(self.bucket)
        if (self.boom < -1.0) or (self.boom > 1.0):
            logger.error('Boom command is not in the input range, should be [-1.0..1.0], but it is {}'.format(self.boom))
            self.boom = 0.0
        boom = HAL_Write.convert_percent_to_int(self.boom)
        register_3 = (boom & 0x00ff) | ((bucket & 0x00ff) << 8)
        #logger.debug('register 3 : {}'.format(format(register_3, '#06x')))

        # register 4 contains : 
        #   LSB : steering
        #   MSB : unused
        # convert from input range [-1.0..1.0] to range [-128..127]
        if (self.steering < -1.0) or (self.steering > 1.0):
            logger.error('Steering command is not in the input range, should be [-1.0..1.0], but it is {}'.format(self.steering))
            self.steering = 0.0 
        steering = HAL_Write.convert_percent_to_int(self.steering)
        register_4 = steering & 0x00ff
        #logger.debug('register 4 : {}'.format(format(register_4, '#06x')))
        
        return [register_0, register_1, register_2, register_3, register_4]       

    @staticmethod
    def import_from_machine(machine_write):
        """
        import_from_machine Import values from a MachineWrite object

        :param machine_write: input object
        :type machine_write: MachineWrite
        :return: converted object
        :rtype: HAL_Write
        """

        # conversions
        if machine_write.gear_speed in HAL_Write.GEAR_SPEED:
            gear_speed = HAL_Write.GEAR_SPEED[machine_write.gear_speed]
        else:
            logger.error('Conversion from MachineWrite to HAL_Write failed due to unknown gear speed {} -> using GS_1ST.'.format(machine_write.gear_speed))
            gear_speed = HAL_Write.GS_1ST

        if machine_write.shift_mode in HAL_Write.SHIFTMODE:
            shift_mode = HAL_Write.SHIFTMODE[machine_write.shift_mode]
        else:
            logger.error('Conversion from MachineWrite to HAL_Write failed due to unknown shift mode {} -> using SM_LOW.'.format(machine_write.shift_mode))
            shift_mode = HAL_Write.SM_LOW

        if machine_write.directional_sel in HAL_Write.DIR_MODE:
            directional_sel = HAL_Write.DIR_MODE[machine_write.directional_sel]
        else:
            logger.error('Conversion from MachineWrite to HAL_Write failed due to unknown directional mode {} -> using DM_NEUTRAL.'.format(machine_write.directional_sel))
            directional_sel = HAL_Write.DM_NEUTRAL

        if machine_write.ppc in HAL_Write.PPC_LOCK_RELEASE:
            ppc = HAL_Write.PPC_LOCK_RELEASE[machine_write.ppc]
        else:
            logger.error('Conversion from MachineWrite to HAL_Write failed due to unknown ppc {} -> using PPC_LOCK_RELEASE_DISABLE.'.format(machine_write.ppc))
            ppc = HAL_Write.PPC_LOCK_RELEASE_DISABLE

        if machine_write.disable_front_lidar in HAL_Write.FRONT_LIDAR:
            disable_front_lidar = HAL_Write.FRONT_LIDAR[machine_write.disable_front_lidar]
        else:
            logger.error('Conversion from MachineWrite to HAL_Write failed due to unknown disable_front_lidar {} -> using FRONT_LIDAR_ENABLE instead'.format(machine_write.disable_front_lidar))
            disable_front_lidar = HAL_Write.FRONT_LIDAR_ENABLE

        # options are already safely checked in import_from_machine_options
        options = HAL_Write.HAL_WriteOptions.import_from_machine_options(machine_write.options)

        return HAL_Write(
            gear_speed, 
            shift_mode, 
            directional_sel, 
            options, 
            machine_write.throttle, 
            machine_write.brake, 
            machine_write.boom, 
            machine_write.bucket, 
            machine_write.steering,
            ppc,
            disable_front_lidar
        )
    
    @staticmethod
    def convert_percent_to_int(percent):
        """
        convert_percent_to_int Convert a percentage value in the range [-1.0..1.0] to the int range [-128..127]

        :param percent: input value, range is [-1.0..1.0]
        :type percent: float
        :return: int value in range [-128..127]
        :rtype: int
        """
        if (percent < -1.0) or (percent > 1.0):
            logger.error('Value to be converted is out of range -> converting 0.0, wrong input value is {}'.format(percent))
            percent = 0.0
        retval = int((percent + 1.0) / 2.0 * 255.0 - 128)
        return retval


"""

    Tests

"""

if __name__ == '__main__':


    ### TEST 0
    """
    # test for percent conversions

    for i in range(-10, 11, 1):
        i_f = i / 10.0
        i_i = HAL_Write.convert_percent_to_int(i_f)
        i_ui = i_i & 0x00ff
        print('in : {} out : {}, binary : {}'.format(i_f, i_i, format(i_ui, '#010b')))
    """

    ### TEST 1
    """
    # test for the HAL_WriteOptions constructor

    # trying one good HAL_Write_Options
    options = HAL_Write.HAL_WriteOptions(
        HAL_Write.HAL_WriteOptions.PARKING_BRAKE_ENABLE,
        HAL_Write.HAL_WriteOptions.ECSS_ENABLE,
        HAL_Write.HAL_WriteOptions.SHIFT_HOLD_SWITCH_ENABLE,
        HAL_Write.HAL_WriteOptions.TM_CUTOFF_ENABLE,
        HAL_Write.HAL_WriteOptions.LIGHTS_ENABLE,
        HAL_Write.HAL_WriteOptions.HORN_ENABLE,
        HAL_Write.HAL_WriteOptions.AUTO_DIG_ENABLE,
        HAL_Write.HAL_WriteOptions.KICK_DOWN_ENABLE
    )
    print(options)

    # another good one
    options = HAL_Write.HAL_WriteOptions(
        HAL_Write.HAL_WriteOptions.PARKING_BRAKE_DISABLE,
        HAL_Write.HAL_WriteOptions.ECSS_DISABLE,
        HAL_Write.HAL_WriteOptions.SHIFT_HOLD_SWITCH_DISABLE,
        HAL_Write.HAL_WriteOptions.TM_CUTOFF_DISABLE,
        HAL_Write.HAL_WriteOptions.LIGHTS_DISABLE,
        HAL_Write.HAL_WriteOptions.HORN_DISABLE,
        HAL_Write.HAL_WriteOptions.AUTO_DIG_DISABLE,
        HAL_Write.HAL_WriteOptions.KICK_DOWN_DISABLE
    )
    print(options)

    # this one should print ERRORS
    options = HAL_Write.HAL_WriteOptions(
        HAL_Write.HAL_WriteOptions.ECSS_ENABLE,
        HAL_Write.HAL_WriteOptions.SHIFT_HOLD_SWITCH_ENABLE,
        HAL_Write.HAL_WriteOptions.TM_CUTOFF_ENABLE,
        HAL_Write.HAL_WriteOptions.LIGHTS_ENABLE,
        HAL_Write.HAL_WriteOptions.HORN_ENABLE,
        HAL_Write.HAL_WriteOptions.AUTO_DIG_ENABLE,
        HAL_Write.HAL_WriteOptions.KICK_DOWN_ENABLE,
        HAL_Write.HAL_WriteOptions.ECSS_ENABLE
    )
    print(options)
    """

    ### TEST 2
    """
    # test for the import_from_machine_options() function

    # that is a correct one
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
    hwo = HAL_Write.HAL_WriteOptions.import_from_machine_options(mo)
    print(hwo)

    # anothe correct one
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
    hwo = HAL_Write.HAL_WriteOptions.import_from_machine_options(mo)
    print(hwo)

    # this one should fail
    mo = MachineWrite.MachineWriteOptions(
        3, 3, 3, 3, 3, 3, 3, 3
    )
    print(mo)
    hwo = HAL_Write.HAL_WriteOptions.import_from_machine_options(mo)
    print(hwo)
    """

    ### TEST 3
    """
    # test for the constructor of HAL_Write

    # options are already tested, not required to be changed here
    hwo = HAL_Write.HAL_WriteOptions(
        HAL_Write.HAL_WriteOptions.PARKING_BRAKE_ENABLE,
        HAL_Write.HAL_WriteOptions.ECSS_ENABLE,
        HAL_Write.HAL_WriteOptions.SHIFT_HOLD_SWITCH_ENABLE,
        HAL_Write.HAL_WriteOptions.TM_CUTOFF_ENABLE,
        HAL_Write.HAL_WriteOptions.LIGHTS_ENABLE,
        HAL_Write.HAL_WriteOptions.HORN_ENABLE,
        HAL_Write.HAL_WriteOptions.AUTO_DIG_ENABLE,
        HAL_Write.HAL_WriteOptions.KICK_DOWN_ENABLE
    )

    # correct first
    hw = HAL_Write(
        HAL_Write.GS_1ST,
        HAL_Write.SM_LOW,
        HAL_Write.DM_NEUTRAL,
        hwo,
        throttle=0.0,
        brake=1.0,
        boom = -1.0,
        bucket = 1.0,
        steering = 0.0,
        ppc=HAL_Write.PPC_LOCK_RELEASE_DISABLE,
        disable_front_lidar=HAL_Write.FRONT_LIDAR_DISABLE
    )
    print(hw)

    # another correct
    hw = HAL_Write(
        HAL_Write.GS_2ND,
        HAL_Write.SM_HIGH,
        HAL_Write.DM_FORWARD,
        hwo,
        throttle=1.0,
        brake=0.0,
        boom = 1.0,
        bucket = -1.0,
        steering = -1.0,
        ppc=HAL_Write.PPC_LOCK_RELEASE_ENABLE,
        disable_front_lidar=HAL_Write.FRONT_LIDAR_ENABLE
    )
    print(hw)

    # another correct
    hw = HAL_Write(
        HAL_Write.GS_3RD,
        HAL_Write.SM_MANUAL,
        HAL_Write.DM_REVERSE,
        hwo,
        throttle=1.0,
        brake=0.0,
        boom = 1.0,
        bucket = -1.0,
        steering = 1.0,
        ppc=HAL_Write.PPC_LOCK_RELEASE_ENABLE,
        disable_front_lidar=HAL_Write.FRONT_LIDAR_ENABLE
    )
    print(hw)

    # another correct
    hw = HAL_Write(
        HAL_Write.GS_4TH,
        HAL_Write.SM_MANUAL,
        HAL_Write.DM_REVERSE,
        hwo,
        throttle=1.0,
        brake=0.0,
        boom = 1.0,
        bucket = -1.0,
        steering = 1.0,
        ppc=HAL_Write.PPC_LOCK_RELEASE_ENABLE,
        disable_front_lidar=HAL_Write.FRONT_LIDAR_ENABLE
    )
    print(hw)

    # now a wrong one 
    hw = HAL_Write(
        9,
        3,
        7,
        hwo,
        throttle=-1.0,
        brake=1.1,
        boom = -1.1,
        bucket = 1.1,
        steering = 10.0,
        ppc=HAL_Write.FRONT_LIDAR_DISABLE,
        disable_front_lidar=HAL_Write.PPC_LOCK_RELEASE_ENABLE
    )
    print(hw)

    # another wrong one 
    hw = HAL_Write(
        9,
        3,
        7,
        hwo,
        throttle=-1.1,
        brake=-0.1,
        boom = 1.1,
        bucket = -1.1,
        steering = -10.0,
        ppc=HAL_Write.FRONT_LIDAR_DISABLE,
        disable_front_lidar=HAL_Write.PPC_LOCK_RELEASE_ENABLE
    )
    print(hw)
    """

    # TEST 4
    """
    """
    # test to check import_from_machine() function

    # options are already checked
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

    # correct one
    mw = MachineWrite(
        MachineWrite.GS_1ST, 
        MachineWrite.SM_HIGH, 
        MachineWrite.DM_FORWARD, 
        mo,
        0.0, 
        0.0, 
        -1.0, 
        -1.0,
        -1.0,
        ppc=MachineWrite.PPC_LOCK_RELEASE_DISABLE,
        disable_front_lidar=MachineWrite.FRONT_LIDAR_DISABLE
    )
    print(mw)
    hw = HAL_Write.import_from_machine(mw)
    print(hw)

    # another correct one
    mw = MachineWrite(
        MachineWrite.GS_2ND, 
        MachineWrite.SM_LOW, 
        MachineWrite.DM_REVERSE, 
        mo,
        1.0, 
        1.0, 
        1.0, 
        1.0,
        1.0,
        ppc=MachineWrite.PPC_LOCK_RELEASE_ENABLE,
        disable_front_lidar=MachineWrite.FRONT_LIDAR_ENABLE
    )
    print(mw)
    hw = HAL_Write.import_from_machine(mw)
    print(hw)

    # another correct one
    mw = MachineWrite(
        MachineWrite.GS_3RD, 
        MachineWrite.SM_MANUAL, 
        MachineWrite.DM_NEUTRAL, 
        mo,
        1.0, 
        1.0, 
        1.0, 
        1.0,
        1.0,
        ppc=MachineWrite.PPC_LOCK_RELEASE_ENABLE,
        disable_front_lidar=MachineWrite.FRONT_LIDAR_ENABLE
    )
    print(mw)
    hw = HAL_Write.import_from_machine(mw)
    print(hw)

    # another correct one
    mw = MachineWrite(
        MachineWrite.GS_4TH, 
        MachineWrite.SM_MANUAL, 
        MachineWrite.DM_NEUTRAL, 
        mo,
        1.0, 
        1.0, 
        1.0, 
        1.0,
        1.0,
        ppc=MachineWrite.PPC_LOCK_RELEASE_ENABLE,
        disable_front_lidar=MachineWrite.FRONT_LIDAR_ENABLE
    )
    print(mw)
    hw = HAL_Write.import_from_machine(mw)
    print(hw)

    # this one should fail
    mw = MachineWrite(
        5, 
        7, 
        11, 
        mo,
        -1.0, 
        -1.0, 
        -1.1, 
        -10.0,
        -1.001,
        0.1,
        0.2
    )
    print(mw)
    hw = HAL_Write.import_from_machine(mw)
    print(hw)

    # also this one should fail
    mw = MachineWrite(
        5, 
        7, 
        11, 
        mo,
        1.1, 
        1.1, 
        1.1, 
        10.0,
        1.001,
        ppc=MachineWrite.PPC_LOCK_RELEASE_DISABLE,
        disable_front_lidar=MachineWrite.FRONT_LIDAR_DISABLE
    )
    print(mw)
    hw = HAL_Write.import_from_machine(mw)
    print(hw)
    print(hw.convert_to_bytes())