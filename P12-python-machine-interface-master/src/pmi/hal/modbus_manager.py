from loguru import logger
import time

from pmi.hal.hal_read import HAL_Read
from pmi.hal.hal_write import HAL_Write

from pymodbus.client.sync import ModbusTcpClient 
from pymodbus.register_write_message import WriteMultipleRegistersResponse
from pymodbus.register_read_message import ReadHoldingRegistersResponse
from pymodbus.exceptions import ModbusIOException


class ModbusManager:

    # modbus configuration
    START_READ_ADDRESS = 0
    START_WRITE_ADDRESS = 0
    NB_READ_REGISTERS = 10
    NB_WRITE_REGISTERS = 5 # used for write requests
    NB_WR_REGISTERS = 6 # used for read requests, 1 bigger than previous because when we write, we do not write heartbeat register, but we want to read it 
    HR_REG_ADDRESS = 5

    # error control
    SUCCESS = 0
    ERROR_SENDER_DISCONNECTED = 1
    ERROR_RECEIVER_DISCONNECTED = 2
    ERROR_REQUEST_FAILED = 3
    ERROR_SENDER_UNDEFINED = 4
    ERROR_RECEIVER_UNDEFINED = 5


    def __init__(self, reader=True, writer=True):
        """
        __init__ Constructor

        :param reader: read client or not ?
        :type reader: Bool
        :param writer: write client or not ?
        :type writer: Bool
        """
        
        # both connections or only 1 way ?
        self.reader = reader
        self.writer = writer

        # modbus clients
        self.__sender = None
        self.__receiver = None

    def connect(self, ip_address, port_sender, port_receiver, timeout=3.0):
        """
        connect Connect the client(s) to the server(s)

        :param ip_address: IP address of the PLC onboard
        :type ip_address: Str
        :param port_sender: Port of the server to write (used only if writer is True in constructor)
        :type port_sender: Int
        :param port_receiver: Port of the server to read (used only if reader is True in constructor)
        :type port_receiver: Int
        :param timeout: timeout for the modbus requests, defaults to 3.0, might trigger a problem in PLC connection if different.
        :type timeout: Float, optional
        :return: True if connection(s) succeeded, False otherwise
        :rtype: Boolean
        """
        retcode_receiver = False
        retcode_sender = False

        # connections
        if self.writer:
            self.__sender = ModbusTcpClient(host=ip_address, port=port_sender, timeout=timeout)
            retcode_sender = self.__sender.connect()
            logger.info('Writer connection : {}'.format(retcode_sender))
        if self.reader:
            self.__receiver = ModbusTcpClient(host=ip_address, port=port_receiver, timeout=timeout)
            retcode_receiver = self.__receiver.connect()
            logger.info('Reader connection : {}'.format(retcode_receiver))

        # retcodes
        if self.reader and self.writer:
            return (retcode_sender & retcode_receiver)
        elif self.reader and not self.writer:
            return retcode_receiver
        elif not self.reader and self.writer:
            return retcode_sender
        else:
            return False

    def disconnect(self):
        """
        disconnect Disconnect the client from the server
        """
        # first close sender
        if self.writer:
            try:
                self.__sender.close()
                logger.info('Sender connection closed.')
            except:
                logger.info('Modbus sender client did not closed properly.')
        else:
            logger.info('No sender to disconnect.')

        # then close receiver
        if self.reader:
            try:
                self.__receiver.close()
                logger.info('Receiver connection closed.')
            except:
                logger.info('Modbus receiver client did not closed properly.')
        else:
            logger.info('No receiver to disconnect.')

    def __write_registers(self, address, values):
        """
        __write_registers Write mutiple registers

        :param address: start address
        :type address: int
        :param values: values
        :type values: list of int16
        :return: Error code : SUCCESS in case of success, ERROR_SENDER_DISCONNECTED in case of the client got disconnected, ERROR_REQUEST_FAILED in case of the request failed for other reasons
        :rtype: Int
        """
        # check if sender is connected
        wr = None
        if self.__sender.is_socket_open() != True:
            logger.error('ModbusClient is not opened.')
            return ModbusManager.ERROR_SENDER_DISCONNECTED
        # then write
        else:
            logger.debug('I write {} at address {}'.format(values, address))
            try:
                wr = self.__sender.write_registers(address, values, unit=1)
            except ModbusIOException as e:
                logger.error('write_registers() ModbusIOException: {}'.format(e))
                return ModbusManager.ERROR_REQUEST_FAILED
            except Exception as e:
                logger.error('write_registers() Exception: {}'.format(e))
                return ModbusManager.ERROR_REQUEST_FAILED

        # analyze returned values
        if wr is None:
            logger.error('Write request returned None.')
            return ModbusManager.ERROR_REQUEST_FAILED
        elif isinstance(wr, WriteMultipleRegistersResponse):
            if not wr.isError():
                return ModbusManager.SUCCESS
            else:
                logger.error('Write request failed : \"{}\", exception code : {}.'.format(wr, wr.exception_code))
                return ModbusManager.ERROR_REQUEST_FAILED
        else:
            logger.error('Write request returned invalid response type : {}'.format(type(wr)))
            return ModbusManager.ERROR_REQUEST_FAILED

    def write(self, hal_write):
        """
        write Write machine orders

        :param hal_write: HAL_Write object that describes the machine orders
        :type hal_write: HAL_Write
        :return: Error code : SUCCESS in case of success, ERROR_SENDER_DISCONNECTED in case of the client got disconnected, ERROR_REQUEST_FAILED in case of the request failed for other reasons
        :rtype: Int
        """
        # make sure we've got a writer defined
        if not self.writer:
            return ModbusManager.ERROR_SENDER_UNDEFINED
        # if yes write registers
        return self.__write_registers(ModbusManager.START_WRITE_ADDRESS, hal_write.convert_to_bytes())

    def write_heartbeat(self, hr):
        """
        write_heartbeat Write the heartbeat value to the register

        :param hr: heartbeat value
        :type hr: uint8 or uint16, but it cannot be greater than 65535, since it is defined on 16 bits in the register
        :return: Error code : SUCCESS in case of success, ERROR_SENDER_DISCONNECTED in case of the client got disconnected, ERROR_REQUEST_FAILED in case of the request failed for other reasons
        :rtype: Int
        """        
        # make sure we've got a writer defined
        if not self.writer:
            return ModbusManager.ERROR_SENDER_UNDEFINED
        # if yes write heartbeat
        return self.__write_registers(ModbusManager.HR_REG_ADDRESS, hr)

    def __read_registers(self, address, count, read_wr=False):
        """
        __read_registers Read multiple registers

        :param address: start address
        :type address: Int
        :param count: number of registers to read
        :type count: Int
        :param read_wr: instead of reading the "read registers", read the "write registers"
        :type read_wr: Boolean. Default to False, meaning we read "read registers"
        :return: Tuple with list of register at pos 0 and timestamp at pos 1 if success, otherwise Tuple with error code : (ERROR_RECEIVER_DISCONNECTED, None) in case of the client got disconnected, (ERROR_REQUEST_FAILED, None) in case of the request failed for other reasons
        :rtype: Tuple
        """
        # get the correct client, depending on which client we want to read : "read registers" or "write registers"
        client = self.__receiver if not read_wr else self.__sender
        err_client = ModbusManager.ERROR_RECEIVER_DISCONNECTED if not read_wr else ModbusManager.ERROR_SENDER_DISCONNECTED

        if client.is_socket_open() != True:
            logger.error('ModbusClient is not opened.')
            return (err_client, None)
        
        # read
        rr = None
        try:
            rr = client.read_holding_registers(address, count=count)
        except ModbusIOException as e:
            logger.error('read_holding_registers() ModbusIOException : {}'.format(e))
            return (ModbusManager.ERROR_REQUEST_FAILED, None)
        except Exception as e:
            logger.error('read_holding_registers() Exception : {}'.format(e))
            return (ModbusManager.ERROR_REQUEST_FAILED, None)
        
        # read timestamp
        tm = time.time()
        
        # decode answer
        if rr is None:
            logger.error('Read request returned None.')
            return (ModbusManager.ERROR_REQUEST_FAILED, None)
        elif isinstance(rr, ReadHoldingRegistersResponse):
            if rr.isError():
                logger.error('Failed to read registers, error : {}'.format(rr))
                return (ModbusManager.ERROR_REQUEST_FAILED, None)
            # successful case
            else:
                return (rr.registers, tm)
        else:
            logger.error('Read request returned invalid response type : {}'.format(type(rr)))
            return (ModbusManager.ERROR_REQUEST_FAILED, None)

    def read_rr(self):
        """
        read_rr Read the "read registers"

        :return: Tuple with HAL_Read object at pos 0 and timestamp at pos 1 if success, otherwise Tuple with error code : (ERROR_RECEIVER_DISCONNECTED, None) in case of the client got disconnected, (ERROR_REQUEST_FAILED, None) in case of the request failed for other reasons
        :rtype: Tuple
        """
        # make sure we've got a reader defined
        if not self.reader:
            return (ModbusManager.ERROR_RECEIVER_UNDEFINED, None)
        # then read
        registers, timestamp = self.__read_registers(ModbusManager.START_READ_ADDRESS, ModbusManager.NB_READ_REGISTERS, read_wr=False)
        if (registers is ModbusManager.ERROR_RECEIVER_DISCONNECTED) or (registers is ModbusManager.ERROR_REQUEST_FAILED):
            return (registers, timestamp) # return the same error code and None
        return (HAL_Read.convert_from_bytes(registers, timestamp), timestamp)

    def read_wr(self):
        """
        read_wr Read the "write registers", basically read what we wrote

        :return: Tuple with list of register at pos 0 and timestamp at pos 1 if success, otherwise Tuple with error code : (ERROR_RECEIVER_DISCONNECTED, None) in case of the client got disconnected, (ERROR_REQUEST_FAILED, None) in case of the request failed for other reasons
        :rtype: Tuple
        """
        # make sure we've got a writer defined, because we do read, but we read on the write server
        if not self.writer:
            return (ModbusManager.ERROR_SENDER_UNDEFINED, None)
        # then read
        return self.__read_registers(ModbusManager.START_WRITE_ADDRESS, ModbusManager.NB_WR_REGISTERS, read_wr=True)

    @staticmethod
    def print_registers(registers):
        """
        print_registers Print the content of registers as bytes

        :param registers: registers
        :type registers: List
        :return: Str representation
        :rtype: Str
        """
        txt = ''
        for i in range(0, len(registers)):
            register = registers[i]
            txt += 'register {}\n'.format(i)
            txt += '\tregister LSB : {}\n'.format(format(register & 0x00ff, '#010b'))
            txt += '\tregister MSB : {}\n'.format(format((register & 0xff00) >> 8, '#010b'))
        return txt


"""

    Tests
    
"""


if __name__ == '__main__':
    import sys
    hal_write = HAL_Write(
        gear_speed=HAL_Write.GS_1ST,
        shift_mode=HAL_Write.SM_HIGH,
        directional_sel=HAL_Write.DM_FORWARD,
        options=HAL_Write.HAL_WriteOptions(
            parking_brake=HAL_Write.HAL_WriteOptions.PARKING_BRAKE_DISABLE,
            ecss_active=HAL_Write.HAL_WriteOptions.ECSS_ENABLE,
            shift_hold_switch=HAL_Write.HAL_WriteOptions.SHIFT_HOLD_SWITCH_ENABLE,
            tm_cutoff=HAL_Write.HAL_WriteOptions.TM_CUTOFF_ENABLE,
            lights=HAL_Write.HAL_WriteOptions.LIGHTS_ENABLE,
            horn=HAL_Write.HAL_WriteOptions.HORN_ENABLE,
            auto_dig=HAL_Write.HAL_WriteOptions.AUTO_DIG_ENABLE,
            kick_down=HAL_Write.HAL_WriteOptions.KICK_DOWN_ENABLE
        ),
        throttle=0.5,
        brake=0.5,
        boom=1.0,
        bucket=0.5,
        steering=0.05,
        ppc=HAL_Write.PPC_LOCK_RELEASE_ENABLE,
        disable_front_lidar=HAL_Write.FRONT_LIDAR_ENABLE
    )

    # first case, 2 ways, in and out, everything should work basically
    logger.info('<<<<<<<<<<< First test case >>>>>>>>>>>>')
    modbus_client = ModbusManager(reader=True, writer=True)
    if modbus_client.connect('localhost', 1502, 1503):
        logger.success('connected')

        if modbus_client.write(hal_write) == ModbusManager.SUCCESS:
            logger.success('wrote hw succesfully')
        else:
            logger.error('could not write hw')

        if modbus_client.write_heartbeat(345) == ModbusManager.SUCCESS:
            logger.success('wrote hr succesfully')
        else:
            logger.error('could not write hr')

        for i in range(0, 1):
            rr, tm = modbus_client.read_rr()
            if rr != ModbusManager.ERROR_RECEIVER_DISCONNECTED \
                and rr != ModbusManager.ERROR_RECEIVER_UNDEFINED \
                and rr != ModbusManager.ERROR_REQUEST_FAILED:
                logger.success('I read RR : {}'.format(rr))
            else:
                logger.error('could not RR')

            wr, tm = modbus_client.read_wr()
            if wr != ModbusManager.ERROR_SENDER_DISCONNECTED \
                and wr != ModbusManager.ERROR_SENDER_UNDEFINED \
                and wr != ModbusManager.ERROR_REQUEST_FAILED:
                logger.success('I read WR : {}'.format(wr))
            else:
                logger.error('could not WR')

            time.sleep(3)
        
        modbus_client.disconnect()
    else:
        logger.error('could not connect.')

    # second case, only writer
    logger.info('<<<<<<<<<<< Second test case >>>>>>>>>>>>')
    modbus_client = ModbusManager(writer=True,reader=False)
    if modbus_client.connect('localhost', 1502, 1503):
        logger.success('connected')

        # should work
        if modbus_client.write(hal_write) == ModbusManager.SUCCESS:
            logger.success('wrote hw succesfully')
        else:
            logger.error('could not write hw')
        
        # should work
        if modbus_client.write_heartbeat(345) == ModbusManager.SUCCESS:
            logger.success('wrote hr succesfully')
        else:
            logger.error('could not write hr')

        for i in range(0, 1):
            # should fail
            rr, tm = modbus_client.read_rr()
            if rr != ModbusManager.ERROR_RECEIVER_DISCONNECTED \
                and rr != ModbusManager.ERROR_RECEIVER_UNDEFINED \
                and rr != ModbusManager.ERROR_REQUEST_FAILED:
                logger.success('I read RR : {}'.format(rr))
            else:
                logger.error('could not RR')

            # should work
            wr, tm = modbus_client.read_wr()
            if wr != ModbusManager.ERROR_SENDER_DISCONNECTED \
                and wr != ModbusManager.ERROR_SENDER_UNDEFINED \
                and wr != ModbusManager.ERROR_REQUEST_FAILED:
                logger.success('I read WR : {}'.format(wr))
            else:
                logger.error('could not WR')

            time.sleep(3)
        
        modbus_client.disconnect()
    else:
        logger.error('could not connect.')
        
     # third case, only reader
    logger.info('<<<<<<<<<<< Third test case >>>>>>>>>>>>')
    modbus_client = ModbusManager(writer=False,reader=True)
    if modbus_client.connect('localhost', 1502, 1503):
        logger.success('connected')

        # should fail
        if modbus_client.write(hal_write) == ModbusManager.SUCCESS:
            logger.success('wrote hw succesfully')
        else:
            logger.error('could not write hw')
        
        # should fail
        if modbus_client.write_heartbeat(345) == ModbusManager.SUCCESS:
            logger.success('wrote hr succesfully')
        else:
            logger.error('could not write hr')

        for i in range(0, 1):
            # should work
            rr, tm = modbus_client.read_rr()
            if rr != ModbusManager.ERROR_RECEIVER_DISCONNECTED \
                and rr != ModbusManager.ERROR_RECEIVER_UNDEFINED \
                and rr != ModbusManager.ERROR_REQUEST_FAILED:
                logger.success('I read RR : {}'.format(rr))
            else:
                logger.error('could not RR')
            
            # should fail
            wr, tm = modbus_client.read_wr()
            if wr != ModbusManager.ERROR_SENDER_DISCONNECTED \
                and wr != ModbusManager.ERROR_SENDER_UNDEFINED \
                and wr != ModbusManager.ERROR_REQUEST_FAILED:
                logger.success('I read WR : {}'.format(wr))
            else:
                logger.error('could not WR')

            time.sleep(3)
        
        modbus_client.disconnect()
    else:
        logger.error('could not connect.')