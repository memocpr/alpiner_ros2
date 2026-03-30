from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pmi.utility.atcom_logging import PMI_logger
from loguru import logger

# initial data
data_init = [
    0b0000000000000001,  
    0b0000000000000001, 
    0b0000000000000001,  
    0b0000000000000001, 
    0b0000000000000001, 
    0b0000000000000001, 
    0b0000000000000001, 
    0b0000000000000001, 
    0b0000000000000001, 
    0b0000000000000001, 
    0b0000000000000001, 
    0b0000000000000001
]

data_init = [
    0b0000000000000001,  
    0x0001,
    0x0102,
    0x3900,
    0x0000,
    0x0000,
    0x0000,
    0x0000

]

if __name__ == '__main__':

    PMI_logger(terminal_lvl='DEBUG', logfile_lvl='DEBUG', logfile_path='../../../log/write-server_{time}.log')

    # server initialization
    store = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, data_init), # holding registers, start address = 0
    )
    context = ModbusServerContext(slaves=store, single=True)

    # start server
    logger.debug('server is starting...')
    server1 = StartTcpServer(context=context, address=('localhost', 1502), allow_reuse_address=True)
