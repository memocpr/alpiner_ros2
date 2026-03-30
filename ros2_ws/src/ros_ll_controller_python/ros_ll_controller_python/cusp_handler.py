import numpy as np
from loguru import logger
import time

class CuspHandler:

    MAX_CNT_FURTHER_DISTANCE_TO_CUSP = 3            # max times a distance to the cusp can be bigger than the one memorized before we reset the arriving_at_cusp flag
    DIST_FROM_LAST_CUSP_TO_RESTART = 3.0            # min distance to be travelled from last cusp to restart detection
    DIST_MIN_ARRIVING_TO_NEW_CUSP = 2.0             # minimum distance to consider arriving at a new cusp
    DEFAULT_VALUE = -1.0                            # default value for distance to next cusp, used to know if a distance is known or not
    DIST_MIN_AT_CUSP = 1.0                          # minimum distance to consider we are at the cusp, used to reset flags
    TIME_MIN_AT_CUSP = 2.0                          # minimum time to stay at the cusp before resetting flags


    def __init__(self):
        self.mem_distance_to_next_cusp = CuspHandler.DEFAULT_VALUE      # memorized distance to next cusp
        self.cnt_further_distance_to_next_cusp = 0                      # counter to allow some margin of error when arriving at the cusp
        self.distance_from_last_cusp = CuspHandler.DEFAULT_VALUE        # distance travelled from last known cusp
        self.currently_at_cusp = False                                  # currently stopped at the cusp, will be reset after a minimum time
        self.arriving_at_cusp = False                                   # currently not at the cusp, but close enough and closing towards it
        self.possible_to_detect_next_cusp = True                        # flag to know if we can detect the next cusp, is set again when enough distance has been travelled from last known cusp
        self.tm_beginning_at_cusp = None                                # timestamp when we arrived at the cusp, used to reset flags after a minimum time
    
    def get_currently_at_cusp(self):
        return self.currently_at_cusp
    
    def get_arriving_at_cusp(self):
        return self.arriving_at_cusp
    
    def set_values_when_cusp_detected(self):
        self.currently_at_cusp = True
        self.possible_to_detect_next_cusp = False # we are at the cusp, we cannot detect the next cusp until we have travelled enough distance from last known cusp
        self.tm_beginning_at_cusp = time.time()
        self.arriving_at_cusp = False
        self.cnt_further_distance_to_next_cusp = 0
        self.distance_from_last_cusp = 0.0
        self.mem_distance_to_next_cusp = CuspHandler.DEFAULT_VALUE

    def update_distance_to_next_cusp(self, distance_to_next_cusp, lin_speed, dt):
        # already at cusp
        if self.currently_at_cusp == True:
            # if we are at the cusp for a minimum time, reset flags
            if self.tm_beginning_at_cusp is None:
                logger.warning('CUSP detected, but no timestamp set yet, setting it now')
                self.tm_beginning_at_cusp = time.time()
            time_at_cusp = time.time() - self.tm_beginning_at_cusp
            if time_at_cusp >= CuspHandler.TIME_MIN_AT_CUSP:
                logger.info('CUSP detected for {} seconds, resetting flags'.format(time_at_cusp))
                self.currently_at_cusp = False # enough time spent at cusp -> allows controller to give throttle FW and BW again
                self.tm_beginning_at_cusp = None

        if self.possible_to_detect_next_cusp == False:
            # compute distance from last cusp
            distance_from_last_cusp = self._compute_distance_from_last_cusp(lin_speed, dt)

            # enough distance has been travelled from last known cusp
            if abs(distance_from_last_cusp) >= CuspHandler.DIST_FROM_LAST_CUSP_TO_RESTART:
                logger.info('reset cusp handler after enough distance has been travelled from last cusp -> reset and return')
                self.possible_to_detect_next_cusp = True # enough distance travelled from last known cusp
                self.tm_beginning_at_cusp = None
                self.currently_at_cusp = False
                self.distance_from_last_cusp = CuspHandler.DEFAULT_VALUE
                return
            else:
                logger.info('not enough distance has been travelled from last cusp : {}'.format(self.distance_from_last_cusp))
                return

        # arriving_at_cusp
        elif (self.arriving_at_cusp == True):
            # actual distance is not known but memorized distance is known -> we are most likely at cusp since we were approaching it
            if (self.mem_distance_to_next_cusp != CuspHandler.DEFAULT_VALUE) and (distance_to_next_cusp == CuspHandler.DEFAULT_VALUE):
                logger.info('CUSP detected : {}'.format(self.mem_distance_to_next_cusp))
                self.set_values_when_cusp_detected()
                return
            
            # both distances are know
            elif (self.mem_distance_to_next_cusp != CuspHandler.DEFAULT_VALUE) and (distance_to_next_cusp != CuspHandler.DEFAULT_VALUE):
                logger.info('arriving at cusp -> compute flags')
                self._check_arriving_conditions(distance_to_next_cusp)
                self.mem_distance_to_next_cusp = distance_to_next_cusp
                return
            
            else:
                logger.warning('not enough information to compute flags, returning')
                return

        # no flag is set
        else:
            # both distances are default values, nothing to do
            if (distance_to_next_cusp == CuspHandler.DEFAULT_VALUE) and (self.mem_distance_to_next_cusp == CuspHandler.DEFAULT_VALUE):
                logger.info('all values are -1.0 -> returning')
                return

            # initializing mem value with new distance value
            elif (distance_to_next_cusp != CuspHandler.DEFAULT_VALUE) and (self.mem_distance_to_next_cusp == CuspHandler.DEFAULT_VALUE):
                logger.info('initializing mem_distance_to_next_cusp with distance_to_next_cusp : {}'.format(distance_to_next_cusp))
                self.mem_distance_to_next_cusp = distance_to_next_cusp
                return
            
            # new value is default value, mem value is known, cant do much with it
            elif (distance_to_next_cusp == CuspHandler.DEFAULT_VALUE) and (self.mem_distance_to_next_cusp != CuspHandler.DEFAULT_VALUE):
                logger.info('new distance to cusp is -1.0 and no flag was set -> reset and returning')
                self.mem_distance_to_next_cusp = CuspHandler.DEFAULT_VALUE

            # default case, both new and mem distances are known
            else:   
                # compute trend towards cusp
                logger.info('normal case, computing flags')
                self._check_arriving_conditions(distance_to_next_cusp)

                # finally memorize distance from cusp
                self.mem_distance_to_next_cusp = distance_to_next_cusp

    def _check_arriving_conditions(self, distance_to_next_cusp):
        # distance is directly small enough, easy case
        if distance_to_next_cusp < CuspHandler.DIST_MIN_AT_CUSP:
            logger.info('CUSP detected because of min distance : {}'.format(distance_to_next_cusp))
            self.set_values_when_cusp_detected()
            return
        
        # we are arriving towards the cusp
        if self.arriving_at_cusp == True:

            # new distance is getting smaller than memorized distance and smaller than threshold
            if (distance_to_next_cusp <= self.mem_distance_to_next_cusp):
                logger.info('distance towards cusp is decreasing : {}'.format(distance_to_next_cusp))
                self.cnt_further_distance_to_next_cusp = 0
                return
            
            # oops, new distance is bigger than memorized distance...
            else:
                self.cnt_further_distance_to_next_cusp += 1
                if self.cnt_further_distance_to_next_cusp >= CuspHandler.MAX_CNT_FURTHER_DISTANCE_TO_CUSP:
                    logger.info('counter reached its top value -> not moving towards cusp anymore...')
                    self.arriving_at_cusp = False
                    self.cnt_further_distance_to_next_cusp = 0
                    return
                else:
                    logger.info('got a bigger distance, but counter still in margin error : {}'.format(self.cnt_further_distance_to_next_cusp))
                    return
                
        # cusp arriving not set yet
        else:
            if (distance_to_next_cusp <= self.mem_distance_to_next_cusp) and (distance_to_next_cusp <= CuspHandler.DIST_MIN_ARRIVING_TO_NEW_CUSP):
                logger.info('arriving close to a new cusp : {}'.format(distance_to_next_cusp))
                self.arriving_at_cusp = True
                self.cnt_further_distance_to_next_cusp = 0
            else:
                logger.info('not arriving at cusp, distance is too big : {}'.format(distance_to_next_cusp))

    def _compute_distance_from_last_cusp(self, lin_speed, dt):
        if self.distance_from_last_cusp == CuspHandler.DEFAULT_VALUE:
            logger.warning('distance_from_last_cusp is not initialized, setting it to 0.0')
            self.distance_from_last_cusp = 0.0
        self.distance_from_last_cusp += lin_speed * dt
        return self.distance_from_last_cusp
