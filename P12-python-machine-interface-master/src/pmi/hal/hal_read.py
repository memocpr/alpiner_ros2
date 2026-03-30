from loguru import logger

class HAL_Read:

    """
    constants to be used in hal world,
    with the Modbus registers.
    for all other usage, check the class MachineRead.
    """
    DM_FORWARD = 0b100
    DM_REVERSE = 0b010
    DM_NEUTRAL = 0b001
    GS_UNDEF = 0b0000
    GS_1ST = 0b0001
    GS_2ND = 0b0010
    GS_3RD = 0b0100
    GS_4TH = 0b1000
    SPEED_SIGN_FW = 0b0
    SPEED_SIGN_REV = 0b1

    class HAL_ReadOthers:

        """
        constants to be used in hal world,
        with the Modbus registers.
        for all other usage, check the class MachineRead.
        """
        OP_MODE_LOCAL = 0b00
        OP_MODE_REMOTE = 0b01
        OP_MODE_AUTO = 0b10
        OP_MODE_EMERGENCY_STOP = 0b11

        ENGINE_STATUS_OFF = 0b0
        ENGINE_STATUS_ON = 0b1

        PARKING_BRAKE_OFF = 0b1 # /!\ inversion
        PARKING_BRAKE_ON = 0b0 # /!\ inversion

        PPC_LOCKED = 0b1
        PPC_RELEASED = 0b0

        SPEED_LIMITATION_ENABLED = 0b1
        SPEED_LIMITATION_DISABLED = 0b0
        
        def __init__(self, op_mode_hw, engine_status, parking_brake, ppc, speed_limitation):
            """
            __init__ Constructor

            :param op_mode_hw: operation mode
            :type op_mode_hw: Int, 00 = local, 01 = remote, 10 = automatic, 11 = emergency stop
            :param engine_status: engine status
            :type engine_status: Int, 0 = off, 1 = on
            :param parking_brake: parking brake
            :type parking_brake: Int, 0 = on, 1 = off
            :param ppc: ppc lock release
            :type ppc: Int, 0 = released, 1 = locked
            :param speed_limitation: speed limitation flag
            :type speed_limitation: Int, 0 = disabled, 1 = enabled
            """
            if (op_mode_hw == HAL_Read.HAL_ReadOthers.OP_MODE_LOCAL) or (op_mode_hw == HAL_Read.HAL_ReadOthers.OP_MODE_REMOTE) or \
                (op_mode_hw == HAL_Read.HAL_ReadOthers.OP_MODE_AUTO) or (op_mode_hw == HAL_Read.HAL_ReadOthers.OP_MODE_EMERGENCY_STOP):
                self.op_mode_hw = op_mode_hw
            else:
                logger.error('unexpected value for op_mode_hw {} -> using OP_MODE_REMOTE instead'.format(op_mode_hw))
                self.op_mode_hw = HAL_Read.HAL_ReadOthers.OP_MODE_REMOTE
            
            if (engine_status == HAL_Read.HAL_ReadOthers.ENGINE_STATUS_OFF) or (engine_status == HAL_Read.HAL_ReadOthers.ENGINE_STATUS_ON):
                self.engine_status = engine_status
            else:
                logger.error('unexpected value for engine status {} -> using ENGINE_STATUS_OFF instead'.format(engine_status))
                self.engine_status = HAL_Read.HAL_ReadOthers.ENGINE_STATUS_OFF

            if (parking_brake == HAL_Read.HAL_ReadOthers.PARKING_BRAKE_OFF) or (parking_brake == HAL_Read.HAL_ReadOthers.PARKING_BRAKE_ON):
                self.parking_brake = parking_brake
            else:
                logger.error('unexpected value for parking brake {} -> using PARKING_BRAKE_OFF instead'.format(parking_brake))
                self.parking_brake = HAL_Read.HAL_ReadOthers.PARKING_BRAKE_OFF
            
            if (ppc == HAL_Read.HAL_ReadOthers.PPC_LOCKED) or (ppc == HAL_Read.HAL_ReadOthers.PPC_RELEASED):
                self.ppc = ppc
            else:
                logger.error('unexpected value for ppc {} -> using PPC_LOCK instead'.format(ppc))
                self.ppc = HAL_Read.HAL_ReadOthers.PPC_LOCKED

            if (speed_limitation == HAL_Read.HAL_ReadOthers.SPEED_LIMITATION_DISABLED) or (speed_limitation == HAL_Read.HAL_ReadOthers.SPEED_LIMITATION_ENABLED):
                self.speed_limitation = speed_limitation
            else:
                logger.error('unexpected value for speed_limitatoin {} -> using SPEED_LIMITATION_DISABLED instead'.format(speed_limitation))
                self.speed_limitation = HAL_Read.HAL_ReadOthers.SPEED_LIMITATION_DISABLED

        def __str__(self):
            return '\n\top mode {}\n\tengine {}\n\tparking brake {}\n\tppc {}\n\tspeed limitation {}\n\t'.format(
                self.op_mode_hw,
                self.engine_status, 
                self.parking_brake,
                self.ppc,
                self.speed_limitation
            )

    class HAL_ReadErrors:

        """
        constants to be used in hal world,
        with the Modbus registers.
        for all other usage, check the class MachineRead.
        by default, no problem is 1.
        """
        ES_BTN_OFF = 0b1
        ES_BTN_ON = 0b0
        ZONE_SAFE_OFF = 0b1
        ZONE_SAFE_ON = 0b0
        OS3_ERROR_REAR_OFF = 0b1
        OS3_ERROR_REAR_ON = 0b0
        OS3_ERROR_FRONT_OFF = 0b1
        OS3_ERROR_FRONT_ON = 0b0
        OS3_WARN_REAR_OFF = 0b1
        OS3_WARN_REAR_ON = 0b0
        OS3_WARN_FRONT_OFF = 0b1
        OS3_WARN_FRONT_ON = 0b0
        OS3_PROTECT_REAR_OFF = 0b1
        OS3_PROTECT_REAR_ON = 0b0
        OS3_PROTECT_FRONT_OFF = 0b1
        OS3_PROTECT_FRONT_ON = 0b0
        BAUMER_OFF = 0b1
        BAUMER_ON = 0b0
        ES_BTN_2_OFF = 0b1
        ES_BTN_2_ON = 0b0
        SHOVEL_POSITION_OFF = 0b1
        SHOVEL_POSITION_ON = 0b0
        HEARTBEAT_OFF = 0b1
        HEARTBEAT_ON = 0b0

        def __init__(self, es_btn, zone_safe, os3_error_rear, os3_error_front, os3_warn_rear, os3_warn_front, \
                     os3_protect_rear, os3_protect_front, baumer, es_btn_2, \
                     shovel_position, heartbeat):
            """__init__ Constructor

            Args:
                es_btn (uint): Emergency stop button
                zone_safe (uint): Zone safe sensor
                os3_error_rear (uint): OS3 error mode rear
                os3_error_front (uint): OS3 error mode front
                os3_warn_rear (uint): OS3 Warning Field reara
                os3_warn_front (uint): OS3 Warning field front
                os3_protect_rear (uint): OS3 protective field rear
                os3_protect_front (uint): OS3 protective field front
                baumer (uint): Baumer sensor 
                es_btn_2 (uint): Emergency stop button 2
                shovel_position (uint): Shovel is in the safe position
                heartbeat (uint): Heartbeat
            """
            self.es_btn = es_btn
            self.zone_safe = zone_safe
            self.os3_error_rear = os3_error_rear
            self.os3_error_front = os3_error_front
            self.os3_warn_rear = os3_warn_rear
            self.os3_warn_front = os3_warn_front
            self.os3_protect_rear = os3_protect_rear
            self.os3_protect_front = os3_protect_front
            self.baumer = baumer
            self.es_btn_2 = es_btn_2
            self.shovel_position = shovel_position
            self.heartbeat = heartbeat
            
        def __str__(self):
            return '\n\tES button -> {}\n\tZone Safe -> {}\n\tOS3 error rear -> {}\n\tOS3 error front -> {}\n\tOS3 warning field rear -> {}\n\tOS3 warning field front -> {} \
                \n\tOS3 protective field rear -> {}\n\tOS3 protective field front -> {}\n\tbaumer -> {}\n\tES button 2 -> {} \
                \n\tShovel position -> {}\n\tHeartbeat -> {}\n\t'.format(
                self.es_btn,
                self.zone_safe,
                self.os3_error_rear,
                self.os3_error_front,
                self.os3_warn_rear,
                self.os3_warn_front,
                self.os3_protect_rear,
                self.os3_protect_front,
                self.baumer,
                self.es_btn_2,
                self.shovel_position,
                self.heartbeat
            )

    def __init__(self, speed, speed_sign, fuel_level, dir_mode, gear_speed, others, errors, boom_angle, bellcrank_angle, \
        steering_angle, heartbeat_sps, boom_lift_pressure, boom_lower_pressure, bucket_digg_pressure, bucket_dump_pressure, \
        boom_lever, bucket_lever, throttle_pedal, brake_pressure, tm = None, registers = None):
        """
        __init__ Constructor

        :param speed: speed of the vehicle
        :type speed: UInt
        :param speed_sign: sign of the speed of the vehicle
        :type speed_sign: UInt
        :param fuel_level: fuel level
        :type fuel_level: UInt
        :param dir_mode: directional mode
        :type dir_mode: UInt
        :param gear_speed: gearbox speed
        :type gear_speed: UInt
        :param others: other bits defined by the protocol
        :type others: HAL_ReadOthers
        :param errors: errors defined by the protocol
        :type errors: HAL_ReadErrors
        :param boom_angle: angle of the boom
        :type boom_angle: UInt
        :param bellcrank_angle: angle of the bellcrank
        :type bellcrank_angle: UInt
        :param steering_angle: angle of the steering
        :type steering_angle: UInt
        :param heartbeat_sps: heartbeat value written by the SPS
        :type heartbeat_sps: UInt
        :param boom_lift_pressure: pression in the boom lift cylinder
        :type boom_lift_pressure: UInt
        :param boom_lower_pressure: pression in the boom lower cylinder
        :type boom_lower_pressure: UInt
        :param bucket_digg_pressure: pression in the bucket digg cylinder
        :type bucket_digg_pressure: UInt
        :param bucket_dump_pressure: pression in the bucket dump cylinder
        :type bucket_dump_pressure: UInt
        :param boom_lever: intensity of the boom lever
        :type boom_lever: UInt
        :param bucket_lever: intensity of the bucket lever
        :type bucket_lever: UInt
        :param throttle_pedal: intensity of the throttle pedal
        :type throttle_pedal: UInt
        :param brake_pressure: pressure in the brake pedal
        :type brake_pressure: UInt
        :param tm: timestamp PMI, aka when the message was read by low level modbus_manager
        :type tm: Float
        :param registers: raw data of the registers, defaults to None
        :type registers: List, optional
        """
        if (speed >= 0) and (speed <= 255):
            self.speed = speed
        else:
            logger.error('unexpected speed value {} -> using 0 instead'.format(speed))
            self.speed = 0

        if (speed_sign == HAL_Read.SPEED_SIGN_FW) or (speed_sign == HAL_Read.SPEED_SIGN_REV):
            self.speed_sign = speed_sign
        else:
            logger.error('unexpected speed sign value {} -> using 0 instead'.format(speed_sign))
            self.speed_sign = HAL_Read.SPEED_SIGN_FW

        if (fuel_level >= 0) and (fuel_level <= 255):
            self.fuel_level = fuel_level
        else:
            logger.error('unexpected fuel level value {} -> using 0 instead'.format(fuel_level))
            self.fuel_level = 0

        if (dir_mode == HAL_Read.DM_FORWARD) or (dir_mode == HAL_Read.DM_NEUTRAL) or \
            (dir_mode == HAL_Read.DM_REVERSE):
            self.directional_mode = dir_mode
        else:
            logger.debug('unexpected directional mode value {} -> not bad, happens between shifts, using DM_NEUTRAL instead'.format(dir_mode))
            self.directional_mode = HAL_Read.DM_NEUTRAL

        if (gear_speed == HAL_Read.GS_1ST) or (gear_speed == HAL_Read.GS_2ND) or \
            (gear_speed == HAL_Read.GS_3RD) or (gear_speed == HAL_Read.GS_4TH) or (gear_speed == HAL_Read.GS_UNDEF):
            self.gear_speed = gear_speed
        else:
            logger.debug('unexpected gear speed value {} -> not bad, happens between shifts'.format(gear_speed))
            self.gear_speed = HAL_Read.GS_UNDEF

        self.others = others
        self.errors = errors

        if (boom_angle >= 0) and (boom_angle <= 255):
            self.boom_angle = boom_angle
        else:
            logger.error('unexpected boom angle value {} -> using 0 instead'.format(boom_angle))
            self.boom_angle = 0

        if (bellcrank_angle >= 0) and (bellcrank_angle <= 255):
            self.bellcrank_angle = bellcrank_angle
        else:
            logger.error('unexpected bellcrank angle {} -> using 0 instead'.format(bellcrank_angle))
            self.bellcrank_angle = 0

        if (steering_angle >= 0) and (steering_angle <= 255):
            self.steering_angle = steering_angle
        else:
            logger.error('unexpected steering angle value {} -> using 0 instead'.format(steering_angle))
            self.steering_angle = 0
        
        if (heartbeat_sps >= 0) and (heartbeat_sps <= 65535):
            self.heartbeat_sps = heartbeat_sps
        else:
            logger.error('unexpected heartbeat sps value {} -> using 0 instead'.format(heartbeat_sps))
            self.heartbeat_sps = 0

        if (boom_lift_pressure >= 0) and (boom_lift_pressure <= 255):
            self.boom_lift_pressure = boom_lift_pressure
        else:
            logger.error('unexpected boom lift pressure {} -> using 0 instead'.format(boom_lift_pressure))
            self.boom_lift_pressure = 0

        if (boom_lower_pressure >= 0) and (boom_lower_pressure <= 255):
            self.boom_lower_pressure = boom_lower_pressure
        else:
            logger.error('unexpected boom lower pressure {} -> using 0 instead'.format(boom_lower_pressure))
            self.boom_lower_pressure = 0

        if (bucket_digg_pressure >= 0) and (bucket_digg_pressure <= 255):
            self.bucket_digg_pressure = bucket_digg_pressure
        else:
            logger.error('unexpected bucket digg pressure {} -> using 0 instead'.format(bucket_digg_pressure))
            self.bucket_digg_pressure = 0

        if (bucket_dump_pressure >= 0) and (bucket_dump_pressure <= 255):
            self.bucket_dump_pressure = bucket_dump_pressure
        else:
            logger.error('unexpected bucket dump pressure {} -> using 0 instead'.format(bucket_dump_pressure))
            self.bucket_dump_pressure = 0

        if (boom_lever >= 0) and (boom_lever <= 255):
            self.boom_lever = boom_lever
        else:
            logger.error('unexpected boom lever intensity {} -> using 0 instead'.format(boom_lever))
            self.boom_lever = 0

        if (bucket_lever >= 0) and (bucket_lever <= 255):
            self.bucket_lever = bucket_lever
        else:
            logger.error('unexpected bucket lever intensity {} -> using 0 instead'.format(bucket_lever))
            self.bucket_lever = 0

        if (throttle_pedal >= 0) and (throttle_pedal <= 255):
            self.throttle_pedal = throttle_pedal
        else:
            logger.error('unexpected throttle pedal intensity {} -> using 0 instead'.format(throttle_pedal))
            self.throttle_pedal = 0

        if (brake_pressure >= 0) and (brake_pressure <= 255):
            self.brake_pressure = brake_pressure
        else:
            logger.error('unexpected brake pressure {} -> using 0 instead'.format(brake_pressure))
            self.brake_pressure = 0

        # timestamp PMI
        self.tm_pmi = tm

        # save registers
        self.registers = registers

    def __str__(self):
        return 'speed -> {}\nspeed sign-> {}\nfuel level -> {}\nboom angle -> {}\nbellcrank angle -> {}\nsteering angle -> {} \
            \nheartbeat sps -> {}\nboom lift pressure -> {}\nboom lower pressure -> {}\nbucket digg pressure -> {}\nbucket dump pressure -> {} \
            \nregisters -> {}\ndir mode -> {}\ngear speed -> {}\nboom lever -> {}\nbucket lever -> {}\nthrottle pedal -> {}\nbrake pressure -> {} \
            \nothers -> {}\nerrors -> {}\ntm_pmi -> {}\n'.format(
                self.speed,
                self.speed_sign,
                self.fuel_level, 
                self.boom_angle,
                self.bellcrank_angle,
                self.steering_angle,
                self.heartbeat_sps,
                self.boom_lift_pressure,
                self.boom_lower_pressure,
                self.bucket_digg_pressure,
                self.bucket_dump_pressure,
                self.registers,
                self.directional_mode,
                self.gear_speed,
                self.boom_lever,
                self.bucket_lever,
                self.throttle_pedal,
                self.brake_pressure,
                self.others, 
                self.errors,
                self.tm_pmi
            ) 
  
    @staticmethod
    def convert_from_bytes(registers, tm=None):
        """
        convert_from_bytes Convert the bytes received (as a List of registers of 2 bytes each) from the server to an object of the class HAL_Read

        :param registers: List returned by the server after a read request, contains 2 bytes per item
        :type registers: List
        :return: an object that represents the state of the machine
        :rtype: HAL_Read
        """
        # register 0 contains :
        register_0 = registers[0]
        #logger.debug('register 0 : {}'.format(format(register_0, '#06x')))

        #   MSB : fuel level    [0..255]
        fuel_level = ((register_0 & 0xff00) >> 8)

        #   LSB : speed         [0..255]
        speed = (register_0 & 0x00ff)

        # register 1 contains : 
        register_1 = registers[1]
        #logger.debug('register 1 : {}'.format(format(register_1, '#06x')))

        #   MSB : others        [res, res, res, res, ppc, parking brake, engine status, operation mode]
        others_byte = (register_1 & 0xff00) >> 8
        op_mode_hw = (others_byte & 0b00000011)      
        engine_status = (others_byte & 0b00000100) >> 2   
        parking_brake = (others_byte & 0b00001000) >> 3       
        speed_limitation = (others_byte & 0b00010000) >> 4
        ppc = (others_byte & 0b00100000) >> 5
        others = HAL_Read.HAL_ReadOthers(op_mode_hw, engine_status, parking_brake, ppc, speed_limitation)

        #   LSB : ECMV fill     [speed_sign, 4th, 3rd, 2nd, 1st, forward, reverse, neutral]
        ecmv_fill = (register_1 & 0x00ff)
        directional_mode = (ecmv_fill & 0b00000111)
        gear_speed = (ecmv_fill & 0b01111000) >> 3
        speed_sign = (ecmv_fill & 0b10000000) >> 7

        # register 2 contains :
        register_2 = registers[2]
        #logger.debug('register 2 : {}'.format(format(register_2, '#06x')))

        #   MSB : error 2       [res, res, res, res, heartbeat, shovel position, baumer, ES btn 2]
        error_2 = (register_2 & 0xff00) >> 8
        #logger.debug('MSB errors : {}'.format(error_2))
        es_btn_2 = (error_2 & 0b00000001)      
        baumer = (error_2 & 0b00000010) >> 1   
        shovel_position = (error_2 & 0b00000100) >> 2   
        heartbeat = (error_2 & 0b00001000) >> 3   

        #   LSB : error 1       [ES btn, zone safe, OS3 error rear, OS3 error front, OS3 warning field rear, OS3 warning field front, OS3 protective field rear, OS3 protective field front]
        error_1 = (register_2 & 0x00ff)
        #logger.debug('LSB errors : {}'.format(error_1))
        os3_protect_front = (error_1 & 0b00000001)      
        os3_protect_rear = (error_1 & 0b00000010) >> 1   
        os3_warn_front = (error_1 & 0b00000100) >> 2   
        os3_warn_rear = (error_1 & 0b00001000) >> 3   
        os3_error_front = (error_1 & 0b00010000) >> 4      
        os3_error_rear = (error_1 & 0b00100000) >> 5       
        zone_safe = (error_1 & 0b01000000) >> 6
        es_btn = (error_1 & 10000000) >> 7
        errors = HAL_Read.HAL_ReadErrors(es_btn, zone_safe, os3_error_rear, os3_error_front, os3_warn_rear, os3_warn_front, \
            os3_protect_rear, os3_protect_front, baumer, es_btn_2, shovel_position, heartbeat)

        # register 3 contains :
        register_3 = registers[3]
        #logger.debug('register 3 : {}'.format(format(register_3, '#06x')))

        #   MSB : bellcrank angle  [0..255]
        bellcrank_angle = (register_3 & 0xff00) >> 8

        #   LSB : boom angle [0..255]
        boom_angle = register_3 & 0x00ff

        # register 4 contains :
        register_4 = registers[4]
        #logger.debug('register 4 : {}'.format(format(register_4, '#06x')))

        #   LSB : steering angle on a 8 bits signed [-128..127] = [-35°..35°]
        steering_angle = register_4 & 0x00ff

        # register 5 contains :
        register_5 = registers[5]
        #logger.debug('register 5 : {}'.format(format(register_5, '#06x')))

        #   LSB : heartbeat_sps
        heartbeat_sps = register_5 & 0xffff

        # register 6 contains :
        register_6 = registers[6]
        #logger.debug('register 6 : {}'.format(format(register_6, '#06x')))

        #   MSB : boom lower pression  [0..255] = [0..510 bars] -> res. = 2 bars/bit
        boom_lower_pressure = (register_6 & 0xff00) >> 8

        #   LSB : boom lift pression [0..255] = [0..510 bars] -> res. = 2 bars/bit
        boom_lift_pressure = register_6 & 0x00ff

        # register 7 contains :
        register_7 = registers[7]
        #logger.debug('register 7 : {}'.format(format(register_7, '#06x')))

        #   MSB : bucket dump pression  [0..255] = [0..510 bars] -> res. = 2 bars/bit
        bucket_dump_pressure = (register_7 & 0xff00) >> 8

        #   LSB : bucket digg pression [0..255] = [0..510 bars] -> res. = 2 bars/bit
        bucket_digg_pressure = register_7 & 0x00ff

        # register 8 contains : 
        register_8 = registers[8]
        #logger.debug('register 8 : {}'.format(format(register_8, '#06x')))

        # MSB : bucket lever intensity [0..255] = [-1.0..1.0]
        bucket_lever = (register_8 & 0xff00) >> 8

        # LSB : boom lever intensity [0..255] = [-1.0..1.0]
        boom_lever = register_8 & 0x00ff

        # register 9 contains : 
        register_9 = registers[9]
        #logger.debug('register 9 : {}'.format(format(register_9, '#06x')))

        # MSB : brake pressure [0..255] = [0..51 bars]
        brake_pressure = (register_9 & 0xff00) >> 8

        # LSB : throttle pedal intensity [0..255] = [0.0..1.0]
        throttle_pedal = register_9 & 0x00ff

        # return an object
        return HAL_Read(speed, speed_sign, fuel_level, directional_mode, gear_speed, others, errors, boom_angle, \
            bellcrank_angle, steering_angle, heartbeat_sps, boom_lift_pressure, boom_lower_pressure, bucket_digg_pressure, \
            bucket_dump_pressure, boom_lever, bucket_lever, throttle_pedal, brake_pressure, tm=tm, registers=registers)


if __name__ == '__main__':
    
    ### TEST 0
    """
    # test HAL_ReadOthers

    # first good ones
    print('Should work as expected.')
    hro = HAL_Read.HAL_ReadOthers(
        HAL_Read.HAL_ReadOthers.OP_MODE_REMOTE,
        HAL_Read.HAL_ReadOthers.ENGINE_STATUS_OFF,
        HAL_Read.HAL_ReadOthers.PARKING_BRAKE_ON,
        HAL_Read.HAL_ReadOthers.PPC_LOCKED
    )
    print(hro)
    print('Should work as expected.')
    hro = HAL_Read.HAL_ReadOthers(
        HAL_Read.HAL_ReadOthers.OP_MODE_AUTO,
        HAL_Read.HAL_ReadOthers.ENGINE_STATUS_ON,
        HAL_Read.HAL_ReadOthers.PARKING_BRAKE_OFF,
        HAL_Read.HAL_ReadOthers.PPC_RELEASED
    )
    print(hro)
    print('Should work as expected.')
    hro = HAL_Read.HAL_ReadOthers(
        HAL_Read.HAL_ReadOthers.OP_MODE_EMERGENCY_STOP,
        HAL_Read.HAL_ReadOthers.ENGINE_STATUS_ON,
        HAL_Read.HAL_ReadOthers.PARKING_BRAKE_ON,
        HAL_Read.HAL_ReadOthers.PPC_LOCKED
    )
    print(hro)
    print('Should work as expected.')
    hro = HAL_Read.HAL_ReadOthers(
        HAL_Read.HAL_ReadOthers.OP_MODE_LOCAL,
        HAL_Read.HAL_ReadOthers.ENGINE_STATUS_OFF,
        HAL_Read.HAL_ReadOthers.PARKING_BRAKE_ON,
        HAL_Read.HAL_ReadOthers.PPC_LOCKED
    )
    print(hro)

    print('Should throw an error !')
    # then a bad one
    hro = HAL_Read.HAL_ReadOthers(
        11, 11, 11, 11
    )
    print(hro)
    """

    """

    ### TEST 1
    """
    # test for the constructor HAL_Read

    # others are already checked
    hro = HAL_Read.HAL_ReadOthers(
        HAL_Read.HAL_ReadOthers.OP_MODE_REMOTE,
        HAL_Read.HAL_ReadOthers.ENGINE_STATUS_OFF,
        HAL_Read.HAL_ReadOthers.PARKING_BRAKE_ON,
        HAL_Read.HAL_ReadOthers.PPC_LOCKED
    )
    # first good ones
    print('Should work as expected.')
    hr = HAL_Read(
        0,
        HAL_Read.SPEED_SIGN_FW,
        0,
        HAL_Read.DM_NEUTRAL,
        HAL_Read.GS_UNDEF,
        hro,
        HAL_Read.HAL_ReadErrors(0,0,0,0,0,0,0,0,0,0,0,0,0,0),
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1.2,
        None
    )
    print(hr)
    print('Should work as expected.')
    hr = HAL_Read(
        0,
        HAL_Read.SPEED_SIGN_REV,
        0,
        HAL_Read.DM_NEUTRAL,
        HAL_Read.GS_1ST,
        hro,
        HAL_Read.HAL_ReadErrors(1,1,1,1,1,1,1,1,1,1,1,1,1,1),
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1.2,
        None
    )
    print(hr)
    print('Should work as expected.')
    hr = HAL_Read(
        255,
        HAL_Read.SPEED_SIGN_FW,
        1,
        HAL_Read.DM_FORWARD,
        HAL_Read.GS_2ND,
        hro,
        HAL_Read.HAL_ReadErrors(1,1,1,1,1,1,1,1,1,1,1,1,1,1),
        255,
        255,
        255,
        65535,
        255,
        255,
        255,
        255,
        255,
        255,
        255,
        255,
        1.2,
        None
    )
    print(hr)
    print('Should work as expected.')
    hr = HAL_Read(
        0,
        HAL_Read.SPEED_SIGN_FW,
        0,
        HAL_Read.DM_REVERSE,
        HAL_Read.GS_3RD,
        hro,
        HAL_Read.HAL_ReadErrors(1,1,1,1,1,1,1,1,1,1,1,1,1,1),
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1.2,
        None
    )
    print(hr)
    print('Should work as expected.')
    hr = HAL_Read(
        0,
        HAL_Read.SPEED_SIGN_FW,
        0,
        HAL_Read.DM_NEUTRAL,
        HAL_Read.GS_4TH,
        hro,
        HAL_Read.HAL_ReadErrors(1,1,1,1,1,1,1,1,1,1,1,1,1,1),
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1.2,
        None
    )
    print(hr)

    # now bad ones
    print('Should throw an error !')
    hr = HAL_Read(
        267,
        267,
        2,
        11,
        11,
        hro,
        HAL_Read.HAL_ReadErrors(1,1,1,1,1,23,1,1,1,1,1,1,1,1),
        267,
        367,
        456,
        345672,
        453,
        256,
        678,
        1245,
        1245,
        546,
        -1,
        657,
        1.2,
        None
    )
    print(hr)



    errors = HAL_Read.HAL_ReadErrors(1,1,1,1,1,23,1,1,1,1,1,1,1,1)
    print(errors)


