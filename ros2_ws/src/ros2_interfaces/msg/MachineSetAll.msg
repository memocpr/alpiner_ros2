uint16 gear_speed 255               # 1-2-3-4
uint16 shift_mode 255               # 5 =Low, 6=Manual, 7 =High
uint16 directional_sel 255          # 8=forward, 9 =Reverse, 10 =Neutral
uint8 ppc 255                       # 0, 1, 255
#uint8 disable_front_lidar 255       # 0, 1, 255
MachineSetOptions options           # check Msg description
float32 throttle 12345.0            # [0.0, 1.0]
float32 brake 12345.0               # [0.0, 1.0]
#float32 boom 12345.0                # [-1.0, 1.0]
#float32 bucket 12345.0              # [-1.0, 1.0]
float32 steering 12345.0            # [-1.0, 1.0] steering intensity in percents
float64 tm_initial_send 0.0         # float64 with the timestamp when the message is originally sent. used to track the latency through all the system
