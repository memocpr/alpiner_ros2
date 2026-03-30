from loguru import logger

class TimeLogger:
    def __init__(self) -> None:
        self.file = None
        self.path = ''
        self.filename = ''

    def init(self, path, filename):
        self.path = path
        self.filename = filename

    def write(self, time):
        try:
            with open(self.path + self.filename, 'a') as file:
                file.write('{}'.format(time))
                file.write('\n')
        except:
            logger.warning('Failed to write time in TimeLogger() : {}'.format(time))