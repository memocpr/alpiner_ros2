from loguru import logger

class EdgeDetection:

    RISING_EDGE_POS = 1     # from 0 to 1
    FALLING_EDGE_POS = 2    # from 1 to 0
    RISING_EDGE_NEG = -1    # from 0 to -1
    FALLING_EDGE_NEG = -2   # from -1 to 0
    NO_EDGE = 0

    @staticmethod
    def detect_edges_3pos(old, new):
        """
        detect_edges_3pos Detect rising/falling edges for 3 positions commands [-1, 0, 1]

        :param old: old value for a gear, mode, ...
        :type old: Int
        :param new: new value for a gear, mode, ...
        :type new: Int
        :return: RISING_EDGE_POS, FALLING_EDGE_POS, RISING_EDGE_NEG, FALLING_EDGE_NEG, NO_EDGE depending on the transition
        :rtype: _type_
        """
        #logger.debug('old : {}, new : {}'.format(old, new))
        if ((old == 0) and (new == 1)) or ((old == -1) and (new == 1)):
            return EdgeDetection.RISING_EDGE_POS
        elif ((old == 0) and (new == -1)) or ((old == 1) and (new == -1)):
            return EdgeDetection.RISING_EDGE_NEG
        elif ((old == 1) and (new == 0)):
            return EdgeDetection.FALLING_EDGE_POS
        elif ((old == -1) and (new == 0)):
            return EdgeDetection.FALLING_EDGE_NEG
        else:
            return EdgeDetection.NO_EDGE

    @staticmethod
    def detect_edges_2pos(old, new):
        """
        detect_edges_2pos Detect rising/falling edges for 2 positions buttons [0, 1]

        :param old: old value for a gear, mode, ...
        :type old: Int
        :param new: new value for a gear, mode, ...
        :type new: Int
        :return: return NO_EDGE, RISING_EDGE_POS, FALLING_EDGE_POS depending on the transition
        :rtype: _type_
        """
        # logger.debug('old : {}, new : {}'.format(old, new))
        if (old == 0) and (new == 1):
            return EdgeDetection.RISING_EDGE_POS
        elif (old == 1) and (new == 0):
            return EdgeDetection.FALLING_EDGE_POS
        else:
            return EdgeDetection.NO_EDGE