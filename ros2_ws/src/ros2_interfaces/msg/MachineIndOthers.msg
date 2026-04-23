uint8 op_mode_hw                # -1 =unknown, 1 =local, 2 = remote, 3 =autonomous, 4 =emergency stop
bool engine_is_on               # if True, engine is ON
bool parking_brake_is_on        # if True, parking brake is ON
bool ppc_is_locked              # if True, PPCis locked, therefore unable to move the boom or bucket
bool speed_limitation           # if True, speed limitation is enabled and speed controller program or so must reduce speed