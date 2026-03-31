from loguru import logger
import numpy as np
import math

from pmi.hal.hal_read import HAL_Read


class MachineRead:

    # constants to be used in machine world and ROS world
    GS_UNDEF = 0
    GS_1ST = 1
    GS_2ND = 2
    GS_3RD = 3
    GS_4TH = 4
    DM_FORWARD = 8
    DM_REVERSE = 9
    DM_NEUTRAL = 10
    SPEED_SIGN_FW = 11
    SPEED_SIGN_REV = 12

    # conversion dicts from HAL world to Machine's world
    GEAR_SPEED = {
        HAL_Read.GS_UNDEF: GS_UNDEF,
        HAL_Read.GS_1ST: GS_1ST,
        HAL_Read.GS_2ND: GS_2ND,
        HAL_Read.GS_3RD: GS_3RD,
        HAL_Read.GS_4TH: GS_4TH,
    }

    DIR_MODE = {
        HAL_Read.DM_FORWARD: DM_FORWARD,
        HAL_Read.DM_REVERSE: DM_REVERSE,
        HAL_Read.DM_NEUTRAL: DM_NEUTRAL,
    }

    SPEED_SIGNS = {
        HAL_Read.SPEED_SIGN_FW : SPEED_SIGN_FW,
        HAL_Read.SPEED_SIGN_REV : SPEED_SIGN_REV
    }

    class MachineReadOthers:
        # constants to be used in machine world and ROS world
        OP_MODE_LOCAL = 1
        OP_MODE_REMOTE = 2
        OP_MODE_AUTO = 3
        OP_MODE_EMERGENCY_STOP = 4
        OP_MODE_UNKNOWN = -1

        ENGINE_STATUS_OFF = False
        ENGINE_STATUS_ON = True

        PARKING_BRAKE_OFF = False
        PARKING_BRAKE_ON = True

        PPC_LOCKED = True
        PPC_RELEASED = False

        SPEED_LIMITATION_ENABLED = True
        SPEED_LIMITATION_DISABLED = False

        # conversion dicts from HAL world to Machine's world
        OP_MODE = {
            HAL_Read.HAL_ReadOthers.OP_MODE_LOCAL: OP_MODE_LOCAL,
            HAL_Read.HAL_ReadOthers.OP_MODE_REMOTE: OP_MODE_REMOTE,
            HAL_Read.HAL_ReadOthers.OP_MODE_AUTO: OP_MODE_AUTO,
            HAL_Read.HAL_ReadOthers.OP_MODE_EMERGENCY_STOP: OP_MODE_EMERGENCY_STOP,
        }

        ENGINE_STATUS = {
            HAL_Read.HAL_ReadOthers.ENGINE_STATUS_OFF: ENGINE_STATUS_OFF,
            HAL_Read.HAL_ReadOthers.ENGINE_STATUS_ON: ENGINE_STATUS_ON,
        }

        PARKING_BRAKE_STATUS = {
            HAL_Read.HAL_ReadOthers.PARKING_BRAKE_OFF: PARKING_BRAKE_OFF,
            HAL_Read.HAL_ReadOthers.PARKING_BRAKE_ON: PARKING_BRAKE_ON,
        }

        PPC_LOCK_RELEASE = {
            HAL_Read.HAL_ReadOthers.PPC_LOCKED: PPC_LOCKED,
            HAL_Read.HAL_ReadOthers.PPC_RELEASED: PPC_RELEASED,
        }

        SPEED_LIMITATION = {
            HAL_Read.HAL_ReadOthers.SPEED_LIMITATION_ENABLED: SPEED_LIMITATION_ENABLED,
            HAL_Read.HAL_ReadOthers.SPEED_LIMITATION_DISABLED: SPEED_LIMITATION_DISABLED,
        }

        def __init__(self, op_mode_hw, engine_status, parking_brake, ppc, speed_limitation):
            """
            __init__ Constructor

            :param op_mode_hw: operation mode
            :type op_mode_hw: expected values [HAL_Read.HAL_ReadOthers.OP_MODE_LOCAL ".".OP_MODE_REMOTE, ".".OP_MODE_AUTO, ".".OP_MODE_EMERGENCY_STOP]
            :param engine_status: engine status
            :type engine_status: expected values [HAL_Read.HAL_ReadOthers.ENGINE_STATUS_OFF, HAL_Read.HAL_ReadOthers.ENGINE_STATUS_ON]
            :param parking_brake: parking brake
            :type parking_brake: expected values [HAL_Read.HAL_ReadOthers.PARKING_BRAKE_OFF, HAL_Read.HAL_ReadOthers.PARKING_BRAKE_ON]
            :param ppc: ppc locked released
            :type ppc: expected values [HAL_Read.HAL_ReadOthers.PPC_LOCKED, HAL_Read.HAL_ReadOthers.PPC_RELEASED]
            :param speed_limitation: speed limitation flag
            :type speed_limitation: exepected values [HAL_Read.HAL_ReadOthers.SPEED_LIMITATION_DISABLED, HAL_Read.HAL_ReadOthers.SPEED_LIMITATION_ENABLED]
            """

            if op_mode_hw in MachineRead.MachineReadOthers.OP_MODE:
                self.op_mode_hw = MachineRead.MachineReadOthers.OP_MODE[op_mode_hw]
            else:
                logger.error(
                    "Conversion from HAL_ReadOthers to MachineReadOthers failed due to bad input {} -> using OP_MODE_LOCAL instead.".format(
                        op_mode_hw
                    )
                )
                self.op_mode_hw = MachineRead.MachineReadOthers.OP_MODE_LOCAL

            if engine_status in MachineRead.MachineReadOthers.ENGINE_STATUS:
                self.engine_status = MachineRead.MachineReadOthers.ENGINE_STATUS[
                    engine_status
                ]
            else:
                logger.error(
                    "Conversion from HAL_ReadOthers to MachineReadOthers failed due to bad input {} -> using ENGINE_STATUS_OFF instead.".format(
                        engine_status
                    )
                )
                self.engine_status = MachineRead.MachineReadOthers.ENGINE_STATUS_OFF

            if parking_brake in MachineRead.MachineReadOthers.PARKING_BRAKE_STATUS:
                self.parking_brake = MachineRead.MachineReadOthers.PARKING_BRAKE_STATUS[
                    parking_brake
                ]
            else:
                logger.error(
                    "Conversion from HAL_ReadOthers to MachineReadOthers failed due to bad input {} -> using PARKING_BRAKE_OFF instead.".format(
                        parking_brake
                    )
                )
                self.parking_brake = MachineRead.MachineReadOthers.PARKING_BRAKE_OFF

            if ppc in MachineRead.MachineReadOthers.PPC_LOCK_RELEASE:
                self.ppc = MachineRead.MachineReadOthers.PPC_LOCK_RELEASE[ppc]
            else:
                logger.error(
                    "Conversion from HAL_ReadOthers to MachineReadOthers failed due to bad input {} -> using PPC_LOCKED instead.".format(
                        ppc
                    )
                )
                self.ppc = MachineRead.MachineReadOthers.PPC_LOCKED

            if speed_limitation in MachineRead.MachineReadOthers.SPEED_LIMITATION:
                self.speed_limitation = MachineRead.MachineReadOthers.SPEED_LIMITATION[speed_limitation]
            else:
                logger.error(
                    "Conversion from HAL_ReadOthers to MachineReadOthers failed due to bad input {} -> using SPEED_LIMITATION_DISABLED instead.".format(
                        speed_limitation
                    )
                )
                self.speed_limitation = MachineRead.MachineReadOthers.SPEED_LIMITATION_DISABLED

        def __str__(self):
            return "\n\top mode {}\n\tengine {}\n\tparking brake {}\n\tppc {}\n\tspeed_limitation {}\n\t".format(
                self.op_mode_hw,
                self.engine_status,
                self.parking_brake,
                self.ppc,
                self.speed_limitation
            )

    class MachineReadErrors:

        # constants to be used in machine world and ROS world
        ES_BTN_OFF = False
        ES_BTN_ON = True
        ZONE_SAFE_OFF = False
        ZONE_SAFE_ON = True
        OS3_ERROR_REAR_OFF = False
        OS3_ERROR_REAR_ON = True
        OS3_ERROR_FRONT_OFF = False
        OS3_ERROR_FRONT_ON = True
        OS3_WARN_REAR_OFF = False
        OS3_WARN_REAR_ON = True
        OS3_WARN_FRONT_OFF = False
        OS3_WARN_FRONT_ON = True
        OS3_PROTECT_REAR_OFF = False
        OS3_PROTECT_REAR_ON = True
        OS3_PROTECT_FRONT_OFF = False
        OS3_PROTECT_FRONT_ON = True
        BAUMER_OFF = False
        BAUMER_ON = True
        ES_BTN_2_OFF = False
        ES_BTN_2_ON = True
        SHOVEL_POSITION_OFF = False
        SHOVEL_POSITION_ON = True
        HEARTBEAT_OFF = False
        HEARTBEAT_ON = True

        def __init__(self, es_btn, zone_safe, os3_error_rear, os3_error_front, os3_warn_rear, os3_warn_front, \
                     os3_protect_rear, os3_protect_front, baumer, es_btn_2, \
                     shovel_position, heartbeat):
            """__init__ Constructor, values are from HAL_Read.HAL_ReadErrors

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
            self.es_btn = MachineRead.MachineReadErrors.ES_BTN_OFF
            if es_btn == HAL_Read.HAL_ReadErrors.ES_BTN_ON:
                self.es_btn = MachineRead.MachineReadErrors.ES_BTN_ON
            elif es_btn != HAL_Read.HAL_ReadErrors.ES_BTN_OFF:
                logger.error('Unexpected value for ES_BTN -> using False instead')

            self.zone_safe = MachineRead.MachineReadErrors.ZONE_SAFE_OFF
            if zone_safe == HAL_Read.HAL_ReadErrors.ZONE_SAFE_ON:
                self.zone_safe = MachineRead.MachineReadErrors.ZONE_SAFE_ON
            elif zone_safe != HAL_Read.HAL_ReadErrors.ZONE_SAFE_OFF:
                logger.error('Unexpected value for Zone safe -> using False instead')

            self.os3_error_rear = MachineRead.MachineReadErrors.OS3_ERROR_REAR_OFF
            if os3_error_rear == HAL_Read.HAL_ReadErrors.OS3_ERROR_REAR_ON:
                self.os3_error_rear = MachineRead.MachineReadErrors.OS3_ERROR_REAR_ON
            elif os3_error_rear != HAL_Read.HAL_ReadErrors.OS3_ERROR_REAR_OFF:
                logger.error('Unexpected value for OS3 error rear -> using False instead')

            self.os3_error_front = MachineRead.MachineReadErrors.OS3_ERROR_FRONT_OFF
            if os3_error_front == HAL_Read.HAL_ReadErrors.OS3_ERROR_FRONT_ON:
                self.os3_error_front = MachineRead.MachineReadErrors.OS3_ERROR_FRONT_ON
            elif os3_error_front != HAL_Read.HAL_ReadErrors.OS3_ERROR_FRONT_OFF:
                logger.error('Unexpected value for OS3 error front -> using False instead')

            self.os3_warn_rear = MachineRead.MachineReadErrors.OS3_WARN_REAR_OFF
            if os3_warn_rear == HAL_Read.HAL_ReadErrors.OS3_WARN_REAR_ON:
                self.os3_warn_rear = MachineRead.MachineReadErrors.OS3_WARN_REAR_ON
            elif os3_warn_rear != HAL_Read.HAL_ReadErrors.OS3_WARN_REAR_OFF:
                logger.error('Unexpected value for OS3 warning rear -> using False instead')

            self.os3_warn_front = MachineRead.MachineReadErrors.OS3_WARN_FRONT_OFF
            if os3_warn_front == HAL_Read.HAL_ReadErrors.OS3_WARN_FRONT_ON:
                self.os3_warn_front = MachineRead.MachineReadErrors.OS3_WARN_FRONT_ON
            elif os3_warn_front != HAL_Read.HAL_ReadErrors.OS3_WARN_FRONT_OFF:
                logger.error('Unexpected value for OS3 warning front -> using False instead')
            
            self.os3_protect_rear = MachineRead.MachineReadErrors.OS3_PROTECT_REAR_OFF
            if os3_protect_rear == HAL_Read.HAL_ReadErrors.OS3_PROTECT_REAR_ON:
                self.os3_protect_rear = MachineRead.MachineReadErrors.OS3_PROTECT_REAR_ON
            elif os3_protect_rear != HAL_Read.HAL_ReadErrors.OS3_PROTECT_REAR_OFF:
                logger.error('Unexpected value for OS3 protect rear -> using False instead')

            self.os3_protect_front = MachineRead.MachineReadErrors.OS3_PROTECT_FRONT_OFF
            if os3_protect_front == HAL_Read.HAL_ReadErrors.OS3_PROTECT_FRONT_ON:
                self.os3_protect_front = MachineRead.MachineReadErrors.OS3_PROTECT_FRONT_ON
            elif os3_protect_front != HAL_Read.HAL_ReadErrors.OS3_PROTECT_FRONT_OFF:
                logger.error('Unexpected value for OS3 protect front -> using False instead')

            self.baumer = MachineRead.MachineReadErrors.BAUMER_OFF
            if baumer == HAL_Read.HAL_ReadErrors.BAUMER_ON:
                self.baumer = MachineRead.MachineReadErrors.BAUMER_ON
            elif baumer != HAL_Read.HAL_ReadErrors.BAUMER_OFF:
                logger.error('Unexpected value for Baumer -> using False instead')

            self.es_btn_2 = MachineRead.MachineReadErrors.ES_BTN_2_OFF
            if es_btn_2 == HAL_Read.HAL_ReadErrors.ES_BTN_2_ON:
                self.es_btn_2 = MachineRead.MachineReadErrors.ES_BTN_2_ON
            elif es_btn_2 != HAL_Read.HAL_ReadErrors.ES_BTN_2_OFF:
                logger.error('Unexpected value for Es btn 2 -> using False instead')

            self.shovel_position = MachineRead.MachineReadErrors.SHOVEL_POSITION_OFF
            if shovel_position == HAL_Read.HAL_ReadErrors.SHOVEL_POSITION_ON:
                self.shovel_position = MachineRead.MachineReadErrors.SHOVEL_POSITION_ON
            elif shovel_position != HAL_Read.HAL_ReadErrors.SHOVEL_POSITION_OFF:
                logger.error('Unexpected value for shovel position -> using False instead')

            self.heartbeat = MachineRead.MachineReadErrors.HEARTBEAT_OFF
            if heartbeat == HAL_Read.HAL_ReadErrors.HEARTBEAT_ON:
                self.heartbeat = MachineRead.MachineReadErrors.HEARTBEAT_ON
            elif heartbeat != HAL_Read.HAL_ReadErrors.HEARTBEAT_OFF:
                logger.error('Unexpected value for heartbeat -> using False instead')

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

    def __init__(self, speed, speed_sign, fuel_level, dir_mode, gear_speed, others, errors, boom_angle, \
        bellcrank_angle, steering_angle, heartbeat_sps, boom_lift_pressure, boom_lower_pressure, \
        bucket_digg_pressure, bucket_dump_pressure, boom_lever, bucket_lever, throttle_pedal, \
        brake_pressure, tm_pmi=None, registers=None):
        """
        __init__ Constructor, all values come from a MachineRead object, and are converted to human readable form for the Display

        :param speed: speed of the vehicle
        :type speed: UInt, converted to Float
        :param speed_sign: sign of the speed of the vehicle
        :type speed_sign: UInt
        :param fuel_level: fuel level
        :type fuel_level: UInt. converted to Float
        :param dir_mode: directional mode
        :type dir_mode: UInt, converted to Int
        :param gear_speed: gearbox speed
        :type gear_speed: UInt, converted to Int
        :param others: other bits defined by the protocol
        :type others: HAL_ReadOthers, converted to MachineReadOthers
        :param errors: errors defined by the protocol
        :type errors: HAL_ReadErrors, converted MachineReadErrors
        :param boom_angle: angle of the boom
        :type boom_angle: UInt, converted to Float
        :param bellcrank_angle: angle of the bellcrank
        :type bellcrank_angle: UInt, converted to Float
        :param steering_angle: angle of the steering
        :type steering_angle: UInt, converted to Float
        :param heartbeat_sps: heartbeat value written by the SPS
        :type heartbeat_sps: Uint16
        :param boom_lift_pressure: pressure in the boom lift cylinder
        :type boom_lift_pressure: UInt, converted to Float
        :param boom_lower_pressure: pressure in the boom lower cylinder
        :type boom_lower_pressure: UInt, converted to Float
        :param bucket_digg_pressure: pressure in the bucket digg cylinder
        :type bucket_digg_pressure: UInt, converted to Float
        :param bucket_dump_pressure: pressure in the bucket dump cylinder
        :type bucket_dump_pressure: UInt, converted to Float
        :param boom_lever: intensity of the boom lever
        :type boom_lever: UInt, converted to Float
        :param bucket_lever: intensity of the bucket lever
        :type bucket_lever: UInt, converted to Float
        :param throttle_pedal: intensity of the throttle pedal
        :type throttle_pedal: UInt, converted to Float
        :param brake_pressure: pressure in the brake pedal
        :type brake_pressure: UInt, converted to Float
        :param tm_pmi: timestamp PMI, aka when the message was read by low level modbus_manager
        :type tm_pmi: Float
        :param registers: raw data of the registers, defaults to None
        :type registers: List, optional
        """
        # convert speed on uint8 to float, and then round it
        self.speed = (((speed / 255.0) * 51.0) / 3.6)
        if speed_sign in MachineRead.SPEED_SIGNS:
            self.speed_sign = MachineRead.SPEED_SIGNS[speed_sign]
        else:
            logger.error('Conversion speed sign {} failed -> using SPEED_SIGN_FW instead'.format(speed_sign))
            self.speed_sign = MachineRead.SPEED_SIGN_FW

        # convert fuel level from uint8 to float, and then round it
        self.fuel_level = fuel_level / 255.0 * 100.0

        # [0..255] to [-40.0°..46.0°]
        self.boom_angle = MachineRead.convert_boom_angle(boom_angle)

        # from [0..255] to [318.0..251.0°]
        self.bellcrank_angle = MachineRead.convert_bellcrank_angle(bellcrank_angle)

        # angle of the bucket
        self.bucket_angle = 0

        # conversion from [-128°..127°] to [-35.0°..35.0°]
        self.steering_angle = MachineRead.convert_steering_angle(MachineRead.convert_unsigned_to_signed(steering_angle))

        # no conversion
        self.heartbeat_sps = int(heartbeat_sps)

        # easy conversion, from [0..255] to [0..510.0 bars] -> res. = 2 bars/bit
        self.boom_lift_pressure = boom_lift_pressure * 2.0
        self.boom_lower_pressure = boom_lower_pressure * 2.0
        self.bucket_digg_pressure = bucket_digg_pressure * 2.0
        self.bucket_dump_pressure = bucket_dump_pressure * 2.0

        # conversion from [0..255] to [-1.0..1.0]
        self.boom_lever = MachineRead.convert_lever_angle(boom_lever)
        self.bucket_lever = MachineRead.convert_lever_angle(bucket_lever)

        # conversion from [0..255] to [0.0..1.0]
        self.throttle_pedal = throttle_pedal / 255.0

        # conversion from [0..255] to [0.0..51.0]
        self.brake_pressure = brake_pressure / 255.0 * 51.0

        # no conversion
        self.registers = registers

        # conversion required for directional mode
        if dir_mode in MachineRead.DIR_MODE:
            self.directional_mode = MachineRead.DIR_MODE[dir_mode]
        else:
            logger.error(
                "Conversion from HAL_Read to MachineRead failed due to bad input {} -> using DM_NEUTRAL instead.".format(
                    dir_mode
                )
            )
            self.directional_mode = MachineRead.DM_NEUTRAL

        # conversion required for gear speed
        if gear_speed in MachineRead.GEAR_SPEED:
            self.gear_speed = MachineRead.GEAR_SPEED[gear_speed]
        else:
            logger.warning(
                "Conversion from HAL_Read to MachineRead failed due to bad input {} -> using GS_UNDEF instead.".format(
                    gear_speed
                )
            )
            self.gear_speed = MachineRead.GS_UNDEF

        # convert others values
        self.others = MachineRead.MachineReadOthers(
            others.op_mode_hw,
            others.engine_status,
            others.parking_brake,
            others.ppc,
            others.speed_limitation
        )

        # convert errors
        self.errors = MachineRead.MachineReadErrors(errors.es_btn, errors.zone_safe, errors.os3_error_rear, \
            errors.os3_error_front, errors.os3_warn_rear, errors.os3_warn_front, errors.os3_protect_rear, \
            errors.os3_protect_front, errors.baumer, \
            errors.es_btn_2, errors.shovel_position, errors.heartbeat)

        # timestamp from HAL
        self.tm_pmi = tm_pmi

    def __str__(self) -> str:
        return "speed -> {}\nfuel level -> {}\nboom angle -> {}\nbellcrank angle -> {}\nbucket angle -> {}\nsteering angle -> {} \
            \nheartbeat sps -> {}\nboom lift pressure -> {}\nboom lower pressure -> {}\nbucket digg pressure -> {}\nbucket dump pressure -> {} \
            \nregisters -> {}\ndir mode -> {}\ngear speed -> {}\nboom lever -> {}\nbucket lever -> {}\nthrottle pedal -> {}\nbrake pressure -> {} \
            \nothers -> {}\nerrors -> {}\ntm_pmi -> {}\n".format(
            self.speed,
            self.fuel_level,
            self.boom_angle,
            self.bellcrank_angle,
            self.bucket_angle,
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
    def import_from_hal_read(hal_read):
        """
        import_from_hal_read convert from HAL_read to MachineRead

        :param hal_read: input object
        :type hal_read: HAL_Read
        :return: converted object
        :rtype: MachineRead
        """
        return MachineRead(
            hal_read.speed,
            hal_read.speed_sign,
            hal_read.fuel_level,
            hal_read.directional_mode,
            hal_read.gear_speed,
            hal_read.others,
            hal_read.errors,
            hal_read.boom_angle,
            hal_read.bellcrank_angle,
            hal_read.steering_angle,
            hal_read.heartbeat_sps,
            hal_read.boom_lift_pressure,
            hal_read.boom_lower_pressure,
            hal_read.bucket_digg_pressure,
            hal_read.bucket_dump_pressure,
            hal_read.boom_lever,
            hal_read.bucket_lever,
            hal_read.throttle_pedal,
            hal_read.brake_pressure,
            hal_read.tm_pmi,
            hal_read.registers,
        )

    @staticmethod
    def convert_unsigned_to_signed(unsigned):
        """
        convert_unsigned_to_signed Interpret an unsigned number into a signed number, by using the raw bytes to convert to 2's complements

        :param unsigned: the unsigned number to convert
        :type unsigned: Uint, max value 255
        :return: signed number, from -128 to 127
        :rtype: Int
        """
        if unsigned > 255:
            logger.warning("Overflow : unsigned int cannot be converted on 1 byte.")
            return 0
        import sys

        b = unsigned.to_bytes(
            1, byteorder=sys.byteorder, signed=False
        )  # convert from unsigned int to bytes
        return int.from_bytes(
            b, byteorder=sys.byteorder, signed=True
        )  # convert from bytes to signed int

    def convert_bellcrank_angle(raw_value):
        """
        convert_bellcrank_angle converts the raw uint8 value to a float value in degree [318.0..251.0°]

        :param raw_value: input value
        :type raw_value: uint8
        :return: converted value
        :rtype: float
        """
        # normalize
        min_angle = 318
        max_angle = 251
        norm_value = raw_value / 255.0
        # bellcrank range is [318..251°]
        angle = norm_value * (max_angle - min_angle)
        return angle + min_angle

    @staticmethod
    def convert_boom_angle(raw_value):
        """
        convert_boom_angle convert the raw uint value to a float value in degree [-40.0°..46.0°]

        :param raw_value: input value
        :type raw_value: uint8
        :return: converted value
        :rtype: float
        """
        # normalize
        min_angle = -40
        max_angle = 46
        norm_value = raw_value / 255.0
        # boom range is [-40°..46°]
        angle = norm_value * (max_angle - min_angle)
        # shift to neg
        return angle + min_angle

    @staticmethod
    def convert_steering_angle(raw_value):
        """
        convert_steering_angle convert the raw int value to a int value in degree [-35.0°..35.0°]

        :param raw_value: input value in range [-128..127]
        :type raw_value: int8
        :return: converted value in range [-35.0°..35.0°]
        :rtype: int
        """
        # normalize
        norm_value = raw_value / 256.0
        # boom range is [-35.0°..35.0°]
        angle = norm_value * 70.0
        return angle

    @staticmethod
    def convert_lever_angle(raw_value):
        """
        convert_lever_angle convert the raw int value to a float value in degree

        :param raw_value: input value in range [-128..127]
        :type raw_value: int8
        :return: converted value in range [-1.0..1.0]
        :rtype: float
        """
        # normalize
        norm_value = raw_value / 255.0  # range is now [0.0..1.0]
        norm_value *= 2.0  # range is now [0.0..2.0]
        norm_value -= 1.0  # range is now [-1.0..1.0]
        return norm_value



"""

    Tests

"""


if __name__ == "__main__":
    ### TEST 0
    """
    # test unsigned to signed conversion
    print('convert_unsigned_to_signed')
    for i in range(0, 256):
        print('{} -> {}'.format(bin(i), MachineRead.convert_unsigned_to_signed(i)))
    # test bellcrank angle conversion
    print('convert_bellcrank_angle')
    for i in range(0, 256):
        print('{} -> {}'.format(bin(i), MachineRead.convert_bellcrank_angle(i)))
    # test boom angle conversion
    print('convert_boom_angle')
    for i in range(0, 256):
        print('{} -> {}'.format(bin(i), MachineRead.convert_boom_angle(i)))
    # test steering angle conversion
    print('convert_steering_angle')
    for i in range(-128, 128):
        print('{} -> {}'.format(bin(i), MachineRead.convert_steering_angle(i)))
    # test lever angle conversion
    print('convert_lever_angle')
    for i in range(-128, 128):
        print('{} -> {}'.format(bin(i), MachineRead.convert_lever_angle(i)))
    """

    ### TEST 1
    """
    # test of full conversion from HAL_read to MachineRead
    """

    # test conversion from registers to hal
    raw_registers = [
        0b0000000000000001,  # reg 0, MSB is fuel level, LSB is speed
        0b0000000011000001,  # reg 1, MSB is [res, res, speed_limitation, ppc, parking brake, engine status, operation mode, operation mode], LSB is [speed sign, 4th, 3rd, 2nd, 1st, forward, reverse, neutral]
        0b0000000000000000,  # reg 2, MSB is error 2 [res, res, res, res, heartbeat, shovel position, baumer, ES btn 2], LSB is error 1 [ES btn, zone safe, OS3 error rear, OS3 error front, OS3 warn rear, Os3 warn front, OS3protect rear, OS3 protect front]
        0b0000000000000000,  # reg 3, MSB is bellcrank angle, LSB is boom angle
        0b0000000000000001,  # reg 4, MSB is None, LSB is steering angle
        0b1000000000000000,  # reg 5, MSB and LSB are heartrate sps, UINT16
        0b0000000100000001,  # reg 6, MSB is Boom lower pressure, LSB is Boom lift pressure
        0b1000000011111111,  # reg 7, MSB is Bucket dump pressure, LSB is Bucket digg pressure
        0b1000000011111111,  # reg 8, MSB is bucket lever, LSB is boom lever pressure
        0b1000000011111111,  # reg 9, MSB is brake pressure, LSB is throttle pedal intensity
    ]
    import time
    hal_read = HAL_Read.convert_from_bytes(raw_registers, tm=time.time())
    print(hal_read)

    # test conversion from hal to machine
    machine_read = MachineRead(
        hal_read.speed,
        hal_read.speed_sign,
        hal_read.fuel_level,
        hal_read.directional_mode,
        hal_read.gear_speed,
        hal_read.others,
        hal_read.errors,
        hal_read.boom_angle,
        hal_read.bellcrank_angle,
        hal_read.steering_angle,
        hal_read.heartbeat_sps,
        hal_read.boom_lift_pressure,
        hal_read.boom_lower_pressure,
        hal_read.bucket_digg_pressure,
        hal_read.bucket_dump_pressure,
        hal_read.boom_lever,
        hal_read.bucket_lever,
        hal_read.throttle_pedal,
        hal_read.brake_pressure,
        hal_read.tm_pmi,
        hal_read.registers,
    )
    print(machine_read)

    machine_read = MachineRead.import_from_hal_read(hal_read)
    print(machine_read)

    ### TEST 2
    """
    # test constructor MachineReadOthers and MachineReadErrors

    # good ones first
    print('This should work !')
    mro = MachineRead.MachineReadOthers(
        HAL_Read.HAL_ReadOthers.OP_MODE_LOCAL,
        HAL_Read.HAL_ReadOthers.ENGINE_STATUS_OFF,
        HAL_Read.HAL_ReadOthers.PARKING_BRAKE_OFF,
        HAL_Read.HAL_ReadOthers.PPC_LOCKED
    )
    print(mro)
    print('This should work !')
    mro = MachineRead.MachineReadOthers(
        HAL_Read.HAL_ReadOthers.OP_MODE_REMOTE,
        HAL_Read.HAL_ReadOthers.ENGINE_STATUS_ON,
        HAL_Read.HAL_ReadOthers.PARKING_BRAKE_ON,
        HAL_Read.HAL_ReadOthers.PPC_RELEASED
    )
    print(mro)
    print('This should work !')
    mro = MachineRead.MachineReadOthers(
        HAL_Read.HAL_ReadOthers.OP_MODE_AUTO,
        HAL_Read.HAL_ReadOthers.ENGINE_STATUS_OFF,
        HAL_Read.HAL_ReadOthers.PARKING_BRAKE_OFF,
        HAL_Read.HAL_ReadOthers.PPC_LOCKED
    )
    print(mro)
    print('This should work !')
    mro = MachineRead.MachineReadOthers(
        HAL_Read.HAL_ReadOthers.OP_MODE_EMERGENCY_STOP,
        HAL_Read.HAL_ReadOthers.ENGINE_STATUS_OFF,
        HAL_Read.HAL_ReadOthers.PARKING_BRAKE_OFF,
        HAL_Read.HAL_ReadOthers.PPC_LOCKED
    )
    print(mro)

    # and now bad one
    print('This must throw an error !')
    mro = MachineRead.MachineReadOthers(11, 12, 13, 14)
    print(mro)


    """
