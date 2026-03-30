from pmi.machine.machine_to_hal.machine_write import MachineWrite
from pmi.machine.hal_to_machine.machine_read import MachineRead

from pmi.hal.modbus_manager import ModbusManager
from pmi.hal.hal_write import HAL_Write
from pmi.hal.hal_read import HAL_Read

from pmi.utility.handler import DataHandler
from pmi.utility.timer import PeriodicTimer
from pmi.utility.atcom_logging import PMI_logger
from pmi.utility.timestamp_handler import TimestampHandler

import time
from loguru import logger


class MachineDriver:
    # timers
    INTERVAL_READ_MACHINE = 0.02 # reading at approx. 50 Hz
    INTERVAL_CHECK_TM = 1.0 # checking oldest TM at 1 Hz
    LATEST_VALID_TM_DELTA = 0.5 # if current time minus latest timestamp is bigger than this, fire callback
    
    # error codes from Modbus
    SUCCESS = ModbusManager.SUCCESS
    ERROR_SENDER_DISCONNECTED = ModbusManager.ERROR_SENDER_DISCONNECTED
    ERROR_RECEIVER_DISCONNECTED = ModbusManager.ERROR_RECEIVER_DISCONNECTED
    ERROR_REQUEST_FAILED = ModbusManager.ERROR_REQUEST_FAILED
    ERROR_SENDER_UNDEFINED = ModbusManager.ERROR_SENDER_UNDEFINED
    ERROR_RECEIVER_UNDEFINED = ModbusManager.ERROR_RECEIVER_UNDEFINED

    def __init__(self, ip_address, port_sender, port_receiver, reader=True, writer=True):
        """
        __init__ Constructor

        :param ip_address: IP address of the PLC on the machine
        :type ip_address: Str
        :param port_sender: Port number of the Modbus server used for write commands
        :type port_sender: Int
        :param port_receiver: Port number of the Modbus server used for read requests
        :type port_receiver: Int
        :param reader: read client or not ?
        :type reader: Bool
        :param writer: write client or not ?
        :type writer: Bool
        """
        # network settings
        self.ip_address = ip_address
        self.port_sender = port_sender
        self.port_receiver = port_receiver

        # handler for read requests with a dedicated timer
        self.__handler_read_rr = None
        self.__handler_read_wr = None
        self.__timer_machine_read = None

        # timestamp management, with another dedicated timer
        self.__handler_timestamp = None
        self.__timer_check_timestamp = None
        self.__callback_check_timestamp = None
        
        # used only in case of manual exit
        self.kill = False

        # in and out, or only in or only out ?
        self.reader = reader
        self.writer = writer
        self.modbus_manager = None

    def init(self, cb_rr, eval_rr, name_eval_rr, cb_wr, eval_wr, name_eval_wr, cb_tm):
        """
        init Init the machine, such as the timers, handlers, ...

        :param cb_rr: callback functions to be fired when the evaluation function returned True when reading "read registers"
        :type cb_rr: List
        :param eval_rr: function to evaluate the change between two read "read registers" response
        :type eval_rr: function
        :param name_eval_rr: name of the evaluation
        :type name_eval_rr: Str
        :param cb_wr: callback functions to be fired when the evaluation function returned True when reading "write registers"
        :type cb_wr: List
        :param eval_wr: function to evaluate the change between two read "write registers" response
        :type eval_wr: function
        :param name_eval_wr: name of the evaluation
        :type name_eval_wr: Str
        :param cb_tm: callback to be fired if the latest timestamp is older than a defined value in MachineConfiguration
        :type cb_tm: function
        :return: True if the Modbus connection succeeded, False otherwise
        :rtype: Boolean
        """
        # connect to the modbus manager
        self.modbus_manager = ModbusManager(self.reader, self.writer)
        retcode = self.modbus_manager.connect(self.ip_address, self.port_sender, self.port_receiver, 3.0)
        if retcode is False:
            return False

        # register read handler
        if self.reader:
            self.__handler_read_rr = DataHandler()
            self.__handler_read_rr.register_evaluation(cb_rr, eval_rr, name_eval_rr)

        # register write handler
        if self.writer:
            self.__handler_read_wr = DataHandler()
            self.__handler_read_wr.register_evaluation(cb_wr, eval_wr, name_eval_wr)

        # timer for read requests
        if self.reader:
            self.__timer_machine_read = PeriodicTimer(MachineDriver.INTERVAL_READ_MACHINE, self.__run)

        # keep track of timestamps
        if self.reader:
            self.__handler_timestamp = TimestampHandler()
            self.__callback_check_timestamp = cb_tm
            self.__timer_check_timestamp = PeriodicTimer(MachineDriver.INTERVAL_CHECK_TM, self.__check_timestamp)

        # heartbeat counter
        self.__counter_heartbeat = 0

        return True

    def start(self, set_machine_motionless=False):
        """
        start Start timers

        :param set_machine_motionless: set the registers to make sure that the machine will not move, defaults to False
        :type set_machine_motionless: Boolean, optional
        """
        # start the timer to read the machine's registers
        if self.reader:
            self.__timer_machine_read.start()

        # start the timer to check the timestamp
        if self.reader:
            self.__timer_check_timestamp.start()

        # set the machine motionless if optional parameter is True
        if self.writer:
            if set_machine_motionless:
                self.set_all(
                    MachineWrite(
                        gear_speed=MachineWrite.GS_1ST,
                        shift_mode=MachineWrite.SM_LOW,
                        directional_sel=MachineWrite.DM_NEUTRAL,
                        options=MachineWrite.MachineWriteOptions(
                            parking_brake=MachineWrite.MachineWriteOptions.PARKING_BRAKE_ENABLE,
                            ecss_active=MachineWrite.MachineWriteOptions.ECSS_ENABLE,
                            shift_hold_switch=MachineWrite.MachineWriteOptions.SHIFT_HOLD_SWITCH_DISABLE,
                            tm_cutoff=MachineWrite.MachineWriteOptions.TM_CUTOFF_DISABLE,
                            lights=MachineWrite.MachineWriteOptions.LIGHTS_DISABLE,
                            horn=MachineWrite.MachineWriteOptions.HORN_DISABLE,
                            auto_dig=MachineWrite.MachineWriteOptions.AUTO_DIG_DISABLE,
                            kick_down=MachineWrite.MachineWriteOptions.KICK_DOWN_DISABLE
                        ),
                        throttle=0.0, 
                        brake=0.0, 
                        boom=0.0, 
                        bucket=0.0, 
                        steering=0.0,
                        ppc=MachineWrite.PPC_LOCK_RELEASE_DISABLE,
                        disable_front_lidar=MachineWrite.FRONT_LIDAR_ENABLE
                    )
                )

                # also set heartbeat
                self.modbus_manager.write_heartbeat(0)

    def __restart(self):
        """
        restart Restart read timer after a disconnection only. The timer check_timestamp is not stopped.
        """
        if self.reader:
            self.__timer_machine_read = PeriodicTimer(MachineDriver.INTERVAL_READ_MACHINE, self.__run)
            self.__timer_machine_read.start()

    def __pause_when_disconnected(self):
        """
        __pause_when_disconnected Kill the timer to read the machine and disconnect correctly when a bad disconnection occurs.
        """
        # stop timer first
        if self.reader:
            self.__timer_machine_read.kill()
            logger.info('Read timer killed due to disconnection.')

        # then kill modbus
        self.modbus_manager.disconnect()

    def stop(self):
        """
        stop Kill the timers and shutdown connections
        """
        self.kill = True
        if self.reader:
            logger.info('Stopping timers...')
            if self.__timer_check_timestamp:
                self.__timer_check_timestamp.kill()
            if self.__timer_machine_read:
                self.__timer_machine_read.kill()
        self.modbus_manager.disconnect()

    def __run(self):
        """
        __run Periodically called from the timer, reads the machine and udpates handlers. Returns in case of errors, but is called again in the next cycle.
        """
        # read registers
        if self.reader:
            hal_read, tm = self.modbus_manager.read_rr()

            # make sure data is valid
            if hal_read is ModbusManager.ERROR_RECEIVER_DISCONNECTED:
                logger.error('RR request failed, ERROR_RECEIVER_DISCONNECTED returned by ModbusManager.read_machine_rr().')
                if not self.kill:
                    self.__handle_disconnections()
                return
            elif hal_read is ModbusManager.ERROR_REQUEST_FAILED:
                logger.error('RR request failed, code ERROR_REQUEST_FAILED returned by ModbusManager.read_machine_rr().')
                if not self.kill:
                    self.__handle_disconnections()
                return

            # update handler, callback will be fired if necessary
            self.__handler_read_rr.update_data(MachineRead.import_from_hal_read(hal_read))

            # also update latest valid timestamp
            if tm is not None:
                self.__handler_timestamp.set_timestamp(tm)

        # read "write registers"
        if self.writer:
            ro, tm = self.modbus_manager.read_wr()
            if ro is ModbusManager.ERROR_SENDER_DISCONNECTED:
                logger.error('WR request failed, ERROR_SENDER_DISCONNECTED returned by ModbusManager.read_machine_wr().')
                if not self.kill:
                    self.__handle_disconnections()
                return 
            elif ro is ModbusManager.ERROR_REQUEST_FAILED:
                logger.error('WR request failed, ERROR_REQUEST_FAILED returned by ModbusManager.read_machine_wr().')
                if not self.kill:
                    self.__handle_disconnections()
                return

            # update handler
            self.__handler_read_wr.update_data(ro)

    def increase_heartbeat(self, heartbeat=None):
        """
        increase_heartbeat Increase the heartbeat in the Modbus server. 
        If heartbeat is not specified, then we use the internal counter.

        :param heartbeat: value to write in server, defaults to None
        :type heartbeat: UInt16, optional
        :return: MachineRead.SUCCESS in case of success,
        or MachineRead.ERROR_SENDER_DISCONNECTED or MachineRead.ERROR_REQUEST_FAILED
        :rtype: Int
        """
        if self.writer:
            value = self.__counter_heartbeat
            if (heartbeat is not None) and (heartbeat <= 65535):
                value = heartbeat
            ret = self.modbus_manager.write_heartbeat(value)
            self.__counter_heartbeat += 1
            if self.__counter_heartbeat > 65535:
                self.__counter_heartbeat = 0
            return ret
        else:
            logger.error('Sender undefined, cant write heartbeat.')
            return MachineDriver.ERROR_SENDER_UNDEFINED

    def __handle_disconnections(self):
        """
        __handle_disconnections Handle disconnections from the Modbus Client
        """
        logger.info("Trying to reconnect to modbus servers !")

        # stop timers first, disconnects all clients
        self.__pause_when_disconnected()

        # wait for a reconnection
        while self.modbus_manager.connect(self.ip_address, self.port_sender, self.port_receiver, timeout=3.0) == False:
            time.sleep(1.0)
            logger.info('Still no connection...')
        logger.info('Connection with Modbus servers is back !')

        # restart timers
        self.__restart()

    def __check_timestamp(self):
        """
        __check_timestamp Periodically called from the timer, and updates timestamp handler
        """
        latest_tm = self.__handler_timestamp.get_timestamp()
        if latest_tm is None:
            return

        # make sure latest tm isn't too old
        tm = time.time()
        if tm - latest_tm > MachineDriver.LATEST_VALID_TM_DELTA:
            logger.debug('Too old timestamp -> firing callback !')
            self.__callback_check_timestamp(tm, latest_tm, True)
        else:
            self.__callback_check_timestamp(tm, latest_tm, False)

    def read_all(self):
        """
        read_all Read the "read registers" without updating handlers, kind of a manual request.

        :return: Tuple with HAL_Read object at pos 0 and timestamp at pos 1 if success, otherwise Tuple with error code : (ERROR_RECEIVER_DISCONNECTED, None) in case of the client got disconnected, (ERROR_REQUEST_FAILED, None) in case of the request failed for other reasons
        :rtype: Tuple
        """
        if self.reader:
            return self.modbus_manager.read_rr()
        else:
            logger.error('Receiver undefined, cant read machine.')
            return (MachineDriver.ERROR_RECEIVER_UNDEFINED, None)

    def set_all(self, machine_write):
        """
        set_all Write "write registers" with the latest commands

        :param machine_write: objects to send to the machine
        :type machine_write: MachineWrite
        :return: Error code : 0 in case of success, 1 in case of the client got disconnected, 3 in case of the request failed for other reasons
        :rtype: Int
        """
        if self.writer:
            return self.modbus_manager.write(HAL_Write.import_from_machine(machine_write))
        else:
            logger.error('Sender undefined, cant write.')
            return (MachineDriver.ERROR_SENDER_UNDEFINED, None)

    def operate_with_logic(self, machine_logic):
        """
        operate_with_logic Translate machine's logic to the machine driver

        :param machine_logic: logic of the machine
        :type machine_logic: MachineLogic
        :return: Error code : 0 in case of success, 1 in case of the client got disconnected, 3 in case of the request failed for other reasons
        :rtype: Int
        """

        # all together
        mw = machine_logic.to_machine_write()
        return self.set_all(mw)


"""
    Tests
"""


# read "read registers" changed
def cb_on_read_rr_changed(data, mem_data):
    logger.debug(data)
    logger.info('received data')


# read "write registers" changed
def cb_on_read_wr_changed(data, mem_data):
    logger.debug(data)


# evaluate read "read registers"
def evaluate_on_read_rr(data, mem_data):
    return True


# evaluate read "write registers"
def evaluate_on_read_wr(data, mem_data):
    return True


# timestamp didn't change
def cb_on_new_timestamp(data, mem_data, flag):
    logger.info('New timestamp ! Flag is {}'.format(flag))

@logger.catch()
def main():
    # setup logger
    PMI_logger(
        terminal_lvl="INFO", logfile_lvl="DEBUG", logfile_path="../../../log/log.txt"
    )

    mw = MachineWrite(
        gear_speed=MachineWrite.GS_1ST,
        shift_mode=MachineWrite.SM_HIGH,
        directional_sel=MachineWrite.DM_FORWARD,
        options=MachineWrite.MachineWriteOptions(
            parking_brake=MachineWrite.MachineWriteOptions.PARKING_BRAKE_DISABLE,
            ecss_active=MachineWrite.MachineWriteOptions.ECSS_ENABLE,
            shift_hold_switch=MachineWrite.MachineWriteOptions.SHIFT_HOLD_SWITCH_ENABLE,
            tm_cutoff=MachineWrite.MachineWriteOptions.TM_CUTOFF_ENABLE,
            lights=MachineWrite.MachineWriteOptions.LIGHTS_ENABLE,
            horn=MachineWrite.MachineWriteOptions.HORN_ENABLE,
            auto_dig=MachineWrite.MachineWriteOptions.AUTO_DIG_ENABLE,
            kick_down=MachineWrite.MachineWriteOptions.KICK_DOWN_ENABLE
        ),
        throttle=0.1,
        brake=0.1,
        boom=0.1,
        bucket=0.1,
        steering=0.1,
        ppc=MachineWrite.PPC_LOCK_RELEASE_ENABLE,
        disable_front_lidar=MachineWrite.FRONT_LIDAR_ENABLE
    )

    logger.info('\n\n<<<<< 1st test case : both reader and writer >>>>>')
    # set up machine
    machine = MachineDriver(ip_address='localhost', port_sender=1502, port_receiver=1503, reader=True, writer=True)
    if machine.init(
        [cb_on_read_rr_changed], 
        evaluate_on_read_rr, 
        'RR TEST', 
        [cb_on_read_wr_changed], 
        evaluate_on_read_wr, 
        'WR TEST', 
        cb_on_new_timestamp
    ):
        logger.success('machine initialized successfully.')

        # start will automatically read machine if reader is set
        machine.start(set_machine_motionless=False)

        # write machine
        if machine.set_all(mw) == ModbusManager.SUCCESS:
            logger.success('Write succeeded')
        else:
            logger.error('Write failed')

        # increase heartbeat
        if machine.increase_heartbeat() == MachineDriver.SUCCESS:
            logger.success('Increased HR')
        else:
            logger.error('Failed to increase HR')

        time.sleep(1.0)

        # stop machine
        machine.stop()
    else:
        logger.error('MachineDriver init failed')

    time.sleep(3.0)
    logger.info('\n\n<<<<< 2nd test case : only writer >>>>>')
    # set up machine
    machine = MachineDriver(ip_address='localhost', port_sender=1502, port_receiver=1503, reader=False, writer=True)
    if machine.init(
        [cb_on_read_rr_changed], 
        evaluate_on_read_rr, 
        'RR TEST', 
        [cb_on_read_wr_changed], 
        evaluate_on_read_wr, 
        'WR TEST', 
        cb_on_new_timestamp
    ):
        logger.success('machine initialized successfully.')

        # start will automatically read machine if reader is set, so not in this case
        machine.start(set_machine_motionless=False)

        # write machine
        if machine.set_all(mw) == ModbusManager.SUCCESS:
            logger.success('Write succeeded')
        else:
            logger.error('Write failed')

        # increase heartbeat
        if machine.increase_heartbeat() == MachineDriver.SUCCESS:
            logger.success('Increased HR')
        else:
            logger.error('Failed to increase HR')

        time.sleep(1.0)

        # stop machine
        machine.stop()
    else:
        logger.error('MachineDriver init failed')

    time.sleep(3.0)
    logger.info('\n\n<<<<< 3rd test case : only reader >>>>>')
    # set up machine
    machine = MachineDriver(ip_address='localhost', port_sender=1502, port_receiver=1503, reader=True, writer=False)
    if machine.init(
        [cb_on_read_rr_changed], 
        evaluate_on_read_rr, 
        'RR TEST', 
        [cb_on_read_wr_changed], 
        evaluate_on_read_wr, 
        'WR TEST', 
        cb_on_new_timestamp
    ):
        logger.success('machine initialized successfully.')

        # start will automatically read machine if reader is set
        machine.start(set_machine_motionless=False)

        # write machine
        if machine.set_all(mw) == ModbusManager.SUCCESS:
            logger.success('Write succeeded')
        else:
            logger.error('Write failed')

        # increase heartbeat
        if machine.increase_heartbeat() == MachineDriver.SUCCESS:
            logger.success('Increased HR')
        else:
            logger.error('Failed to increase HR')

        time.sleep(1.0)

        # stop machine
        machine.stop()
    else:
        logger.error("MachineDriver init failed")


if __name__ == "__main__":
    main()
