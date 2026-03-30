import threading

class TimestampHandler():

    def __init__(self):
        """
        __init__ Constructor
        """
        self.__timestamp = None
        self.__mutex = threading.Lock()

    def get_timestamp(self):
        """
        get_timestamp Get the timestamp value, through the mutex

        :return: timestamp
        :rtype: Float
        """
        self.__mutex.acquire()
        tm = self.__timestamp
        self.__mutex.release()
        return tm

    def set_timestamp(self, tm):
        """
        set_timestamp Set the timestamp, through the mutex

        :param tm: timestamp
        :type tm: Float
        """
        self.__mutex.acquire()
        self.__timestamp = tm
        self.__mutex.release()
