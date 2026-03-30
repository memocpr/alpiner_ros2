from loguru import logger

class DataEvaluation:

    def __init__(self, callbacks, eval_func, name):
        """
        __init__ Constructor

        :param callbacks: list of callbacks to be fired when an evaluation returned True
        :type callbacks: List
        :param eval_func: function to evaluate a data
        :type eval_func: Function
        :param name: name of the evaluation
        :type name: Str
        """
        self.__callbacks = callbacks
        self.evaluation_function = eval_func
        self.name = name

    def fire(self, data, mem_data):
        """
        fire Fire the callbacks when the evaluation function returned True

        :param data: the new data to pass to the callback
        :type data: any, as long as it is supported by the callback function
        :param mem_data: the old data to pass to the callback
        :type mem_data: any, as long as it is supported by the callback function
        """
        for cb in self.__callbacks:
            cb(data, mem_data)

class DataHandler:

    def __init__(self):
        """
        __init__ Constructor
        """
        self.__evaluations = []
        self.__mem_data = None

    def register_evaluation(self, callbacks, eval_func, name='undefined'):
        """
        register_evaluation Register a new DataEvaluation object

        :param callbacks: callback functions
        :type callbacks: List
        :param eval_func: evaluation function
        :type eval_func: Function
        :param name: name to identify the DataEvaluation, defaults to 'undefined'
        :type name: Str, optional
        """
        self.__evaluations.append(DataEvaluation(callbacks=callbacks, eval_func=eval_func, name=name))

    def update_data(self, data):
        """
        update_data Update the DataHandler with a new data

        :param data: new data
        :type data: any, as long as it is supported by both the evaluation function and callback function
        """
        for evaluation in self.__evaluations:
            # first data registered, it is a change -> fire callback
            if self.__mem_data is None:
                logger.debug('Memorized data is None -> firing callback')
                evaluation.fire(data, self.__mem_data)

            # evaluate data with new data
            elif evaluation.evaluation_function(data, self.__mem_data) is True:
                #logger.debug('Evaluate function {} returned True -> firing callback'.format(evaluation.name))
                evaluation.fire(data, self.__mem_data)

        # update memorized data
        self.__mem_data = data
    

"""
    Tests
"""


# equal function
def evaluate_on_unequal(new_int, mem_int):
    return (new_int != mem_int)

# callback for the unequal function
def cb_on_unequal(new_data, mem_data):
    print('new_data on unequal: {}, old data : {}'.format(new_data, mem_data))

# smaller function
def evaluate_on_smaller(new_int, mem_int):
    return (new_int < mem_int)

# callback for the smaller function
def cb_on_smaller(new_data, mem_data):
    print('new_data on smaller: {}'.format(new_data))

# bigger function
def evaluate_on_bigger(new_int, mem_int):
    return (new_int > mem_int)

# callback for the bigger function
def cb_on_bigger(new_data, mem_data):
    print('new_data on bigger: {}'.format(new_data))


# only for testing purposes
if __name__ == '__main__':
    # setup test handler
    handler = DataHandler()
    handler.register_evaluation(callbacks=[cb_on_unequal], eval_func=evaluate_on_unequal, name='[UNEQUAL]')
    handler.register_evaluation(callbacks=[cb_on_smaller, cb_on_unequal], eval_func=evaluate_on_smaller, name='[SMALLER, UNEQUAL]')
    handler.register_evaluation(callbacks=[cb_on_bigger, cb_on_unequal], eval_func=evaluate_on_bigger, name='[BIGGER, UNEQUAL]')

    print('TEST1 : initial data, all callbacks must be fired')
    handler.update_data(10)

    print('TEST2 : same data, none must not be fired')
    handler.update_data(10)

    print('TEST3 : bigger data, only UNEQUAL and BIGGER must be fired')
    handler.update_data(11)

    print('TEST4 : same data, none must not be fired')
    handler.update_data(11)

    print('TEST5 : smaller data, only UNEQUAL and SMALLER must be fired')
    handler.update_data(9)

