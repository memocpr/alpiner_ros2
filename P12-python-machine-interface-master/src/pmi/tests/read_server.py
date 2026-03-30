from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pmi.utility.atcom_logging import PMI_logger
from loguru import logger

# test
data_init = [
    0b0000000000000000, # looks like it is not taken into account by pymodbus when configuring datastore (confirmed with kscada client, the first uint16 given here is not the first register in the server)
    0b0111111100010011, # reg 0, MSB is fuel level, LSB is speed 
    0b0100001000001001, # reg 1, MSB is [pedestrian, PPC, emergency, shovel, parking brake, engine status, operation mode, operation mode], LSB is [res, 4th, 3rd, 2nd, 1st, forward, reverse, neutral] 
    0b0000000000000000, # reg 2, MSB is error 2 [res, res, res, res, res, res, res, res], LSB is error 1 [res, res, res, res, res, res, res, steering]
    0b1101110100000111, # reg 3, MSB is bucket angle, LSB is boom angle
    0b0000000000111111, # reg 4, MSB is None, LSB is steering angle
    0b1111111111111111, # reg 5, MSB and LSB are heartrate sps, UINT16
    0b1000000000000001, # reg 6, MSB is Boom lower pression, LSB is Boom lift pression
    0b1111111001111111, # reg 7, MSB is Bucket dump pression, LSB is Bucket digg pression
    0b1111111111111111, # reg 8, MSB is bucket lever, LSB is boom lever pressure
    0b1000000011111111, # reg 9, MSB is brake pressure, LSB is throttle pedal intensity
    0b1111111111111111, 
    0b1111111111111111, 
    0b1111111111111111
]

"""
corrupted data
data_init = [
    0b0000000000000000, # looks like it is not taken into account by pymodbus when configuring datastore (confirmed with kscada client, the first uint16 given here is not the first register in the server)
    0xa900,
    0x0d01,
    0x0000,
    0xff2d,
    0x007c,
    0xe2e5,
    0x0119,
    0x0305,
    0x0000,
    0x0000,
    0x0000,
    0x0000
]
"""

if __name__ == '__main__':

    PMI_logger(terminal_lvl='DEBUG', logfile_lvl='DEBUG', logfile_path='../../../log/read-server_{time}.log')

    # server initialization
    store = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, data_init), # holding registers, start address = 0
    )
    context = ModbusServerContext(slaves=store, single=True)

    # start server
    logger.debug('server is starting...')
    server1 = StartTcpServer(context=context, address=('localhost', 1503), allow_reuse_address=True)
