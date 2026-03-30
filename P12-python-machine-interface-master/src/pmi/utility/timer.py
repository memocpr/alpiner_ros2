import time
from threading import Thread
from loguru import logger


class PeriodicTimer(Thread):
    """
    simulates the behavior of threading.Timer
    """

    def __init__(self, period, func):
        super(PeriodicTimer, self).__init__()
        self.period = period
        self.func = func
        self.do_run = True

    def run(self):
        while self.do_run:
            delay = self.period - (time.time() % self.period)
            time.sleep(delay)
            self.func()

    def kill(self):
        """
        kill Cancel the timer
        """
        self.do_run = False
        logger.info('do_run is now False in Timer, however current request might still be working -> ERROR will be handled by ModbusManager.')
