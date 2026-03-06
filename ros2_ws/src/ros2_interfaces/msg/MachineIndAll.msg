float32 speed                       # m/s, positive (forward) or negative (backward)
int16 speed_sign                    # 11 = Forward, 12 = Reverse
bool flag_speed_signing_uncertain   # if True, speed is positive, but might as well be negative in reality
float32 angular_velocity            # rad/s, computed from linear speed and steering angle
#float32 fuel_level                  # %
int16 directional_mode              # 8 = Forward, 9 =Reverse, 10 = Neutral
int16 gear_speed                    # 1-2-3-4
MachineIndOthers others             # check Msg description
MachineIndErrors errors             # check Msg description
#float32 boom_angle                  # degrees
#float32 bucket_angle                # degrees
float32 bellcrank_angle             # degrees
float32 steering_angle              # degrees
uint16 heartbeat_sps                # counter
#float32 boom_lift_pressure          # bar
#float32 boom_lower_pressure         # bar
#float32 bucket_digg_pressure        # bar
#float32 bucket_dump_pressure        # bar
#float32 boom_lever                  # [-1.0, 1.0]
#float32 bucket_lever                # [-1.0, 1.0]
float32 throttle_pedal              # [0.0, 1.0]
float32 brake_pressure              # bar
uint16[10] registers                # all raw Modbus registers
float64 tm_pmi                      # timestamp when Modbus request is done
float64 tm_ros                      # timestamp when the conversion PMIROS is done

