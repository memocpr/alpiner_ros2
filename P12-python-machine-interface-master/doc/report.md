# Python Machine Interface PMI

## Introduction

This repository contains the software interface that enables the remote driving of the vehicle. It is written in Python and is based on a Modbus communication. 

## Related documentation

1. `README.md` from [this repository](https://github.com/syrto-AG/P12-python-machine-interface/blob/master/README.md).
2. `README.md` from the [`P12-ros-bridge-2-machine`](https://github.com/syrto-AG/P12-ros-bridge-2-machine/blob/main/README.md).
3. Main documentation of the project, available [here](https://github.com/syrto-AG/P12-documentation/blob/master/src/resources/software/ros/overview.rst#bridge-towards-modbus)

## Overview

The vehicle is normally driven by an operator. In order to make it possible to drive it remotely, a PLC has been installed. This PLC has a direct access to the vehicle's system. All the required commands to drive the machine are sent via Modbus registers of a first server. Also, all the data about the vehicle is similarly encoded in a 2nd server.

## Network

In order to be able to connect to the PLC, you must be in the same subnet as the PLC. The subnet is accessible accessible through two ways : 

1. Local connection : you plug your computer directly to the machine through the available ethernet cable, and you need to select an address in the subnet, such as `172.22.62.96`.
2. Using the wireguard VPN (info [here](https://github.com/syrto-AG/P12-documentation/blob/master/src/site/network/wireguard.rst)), you log into the main computer, IP address is `10.8.0.5` and then you can access the PLC via its local address `172.22.62.12`.

The subnet is `172.22.62.0/24`. The IP address of the PLC is `172.22.62.12`, and the servers are accessible through the port 502 and 503. 

Other addresses in use in the subnet are (not limited to !) : 
- `172.22.62.99` : main computer, containing our ROS2 workspace
- `172.22.62.97` : Jetson Xavier for Soliton camera streaming
- `172.22.62.1` : Siemens 5G gateway
- and many more, especially between `172.22.62.1` and `172.22.62.40`. 

Always make sure to avoid IP address conflicts when connecting devices to the subnet. You can run `nmap -sn 172.22.62.0/24` to list all connected devices.

## Protocol description

There are 2 Modbus servers. One holds the registers to send commands to the vehicle, it is known as the *write server*, or WR server, while the other provides the user with data from the sensors mounted on the vehicle, known as the *read server*, RR server. Therefore, two clients are needed in order to interact with the vehicle.

All registers are holding registers, 16 bits long, which we divide in two bytes, MSB and LSB. Only heartbeats are encoded on the whole 16 bits of the register.

When describing an Uint8 or Uint16 byte, this notation is used : 

- `0` or `1` as per usual
- `u` for an *unused* bit
- `x` for a *not concerned by the description* bit

For example, `uu001xxx` means the bits [7:6] are unused in this byte, the bits [5:3] represent a particular mode or function that interests us, and the bits [2:0] represent another mode or function, that we do not care at this point.

### Write server

- Register 0

    | Position | Name | Encoding | Description | Notes |
    | --- | ----------- | ----------- | ----------- | ----------- |
    | MSB | Shift mode | bits [7:2] are unused, bits [1:0] : shift mode | uuuuuu00 is **low**, uuuuuu01 is **manual**, uuuuuu10 is **high** | **Low** and **high** are automatic modes to shift gears. **Low** shifts low in the RPM, making it more efficient in terms of fuel consumption. **High** shifts higher in the RPM, making it more powerful, but also consumes more fuel. |
    | LSB | Gear speed | bits [7:4] are unused, bits [3:0] : gear speed | uuuu0001 is **1st** gear, uuuu0010 is **2nd** gear, uuuu0100 is **3rd** gear, uuuu1000 is **4th** gear | If the vehicle is set in **low** or **high** shift mode, this is the upper limit of gear speed used, meaning it won't shift any higher. Also, the 4 gears can be used in both **forward** and **reverse** mode. |

- Register 1

    | Position | Name | Encoding | Description | Notes |
    | --- | ----------- | ----------- | ----------- | ----------- |
    | MSB | Options | bit [7] : kick down, bit [6] : auto dig, bit [5] : horn, bit [4] : lights, bit [3] : T/M cutoff, bit[2] : shift hold switch, bit [1] : ECSS active, bit [0] : parking brake disable | See below |  |
    | LSB | Directional mode | bits [7:5] are unused, bit 4 is disable lidar and throttle limit, bit 3 is PPC lock/release, bits [2:0] : directional mode, | uuu1xxxx means disabling lidars and throttle limit during a fixed time, uuu0xxxx means lidar and throttle limit is enabled, uuux1xxx means locking PPC, uuux0xxx means release PPC, uuuxx001 is **neutral**, uuuxx010 is **reverse**, uuuux100 is **forward** | If the vehicle is in **forward** or **reverse** mode, but the driver is applying more pressure on the brake than a threshold (can be set up in the vehicle's settings), it shifts to **neutral**. |

    - Kick down

        Value `1` is launching the procedure **auto dig**. Value `0` does nothing. It is necessary to activate the **auto dig** mode in order to launch the procedure. The vehicle will shift down in **1st** gear and start it, if all necessary conditions are met.

    - Auto dig

        Value `1` means the **auto dig** mode is ON. Value `0` means it is OFF. If the mode is ON, when the **kick down** bit is `1`, then it tries to launch the auto digging procedure. Otherwise it does nothing.

    - Horn

        Value `1` means the **horn** is ON. Value `0` means the **horn** is OFF.
    
    - Lights

        Value `1` means the **lights** is ON. Value `0` means the **lights** is OFF.

    - T/M cutoff

        Value `1` means the vehicle shift to **neutral** mode with active braking. Value `0` does nothing. To be clarified with Lukas for the exact function, not useful so far.

    - Shift hold switch

        Value `1` prevents upshifts from the vehicle. Value `0` does nothing. Only useful and effective in **low** or **high** shift modes.

    - ECSS

        Value `1` means the Electronic Control Suspension System is ON. Value `0` means it is OFF. If the speed is higher than 5km/h, the bucket and boom are balanced by the **ECSS** if it ON. Lower than 5km/h is does nothing, because it probably means the operator is doing a loading or unloading operation, which requires precision.

    - Parking brake

        Value `1` means disabling the **parking brake**. Value `0` means activating the **parking brake**. Be careful  of the inversion of value, `1` being OFF, `0` being ON.

- Register 2

    | Position | Name | Encoding | Description | Notes |
    | --- | ----------- | ----------- | ----------- | ----------- |
    | MSB | Brake | [0..255] means [0..100%] of the braking power |  |  |
    | LSB | Throttle | [0..255] means [0..100%] of the throttle power |  | Throttle is useful not only to move the vehicle forward or reverse, but also to lift the bucket and boom, and steering. |

- Register 3

    | Position | Name | Encoding | Description | Notes |
    | --- | ----------- | ----------- | ----------- | ----------- |
    | MSB | Bucket | [-128..127] is [-100%..100%] of the bucket cylinder power, encoded in two's complement |  |  |
    | LSB | Boom | [-128..127] is [-100%..100%] of the boom cylinder power, encoded in two's complement |  |  |

- Register 4

    | Position | Name | Encoding | Description | Notes |
    | --- | ----------- | ----------- | ----------- | ----------- |
    | MSB |  |  |  |  |
    | LSB | Steering | [-128..127] is [-100%..100%] of the steering cylinder power, encoded in two's complement |  | Negative goes to left. |

- Register 5

    | Position | Name | Encoding | Description | Notes |
    | --- | ----------- | ----------- | ----------- | ----------- |
    | MSB | Heartbeat | Encoded as an Uint16 value | Written at 10Hz by the user, checked periodically by the PLC on the vehicle (currently each 300ms). If it remains unchanged longer than this delay, the safety braking procedure is launched by the PLC. |  |
    | LSB | Heartbeat |  |  |  |

### Read server

- Register 0

    | Position | Name | Encoding | Description | Notes |
    | --- | ----------- | ----------- | ----------- | ----------- |
    | MSB | Fuel level | [0..255] is [0..100%] of fuel level |  | It is the raw value from the sensor. It means that it changes a lot when the vehicle it moving, with the movements of the fuel in the tank. |
    | LSB | Speed | [0..255] is [0..51km/h] |  | Always positive, one must check the **forward** or **reverse** mode in the read server to find the direction. |

- Register 1

    | Position | Name | Encoding | Description | Notes |
    | --- | ----------- | ----------- | ----------- | ----------- |
    | MSB | Others | bit [7] : unused, bit [6] : unused, bit [5] : PPC locked/released, bit [4] : throttle limitation, bit [3] : parking brake, bit [2] : engine status, bits [1:0] : operation mode | see below |  |
    | LSB | ECMV | bit [7] : speed sign, bit [6:3] : gear speed, bit [2:0] : directional mode | u0001xxx is **1st** gear, u0010xxx is **2nd** gear, u0100xxx is **3rd** gear, u1000xxx is **4th** gear, uxxxx001 is **neutral** mode, uxxxx010 is **reverse** mode, uxxxx100 is **forward** mode |  |

    - Speed sign

        Value `1` means reverse, value `0` means forward or stopped. Be careful when using it with small speeds around 0 km/h, it is not sensitive enough.

    - Throttle limitation

        Value `1` means throttle limitation is enabled, and high level user (such as speed controller) should reduce speed, value `0` means throttle limitation is disabled. The reasons why it is activated can be : LiDARs detected an object in the warning field, or the boom bucket is not in the right position
    
    - PPC locked/released

        Value `1` means locked, value `0` means released.

    - Parking brake

        Value `1` means it is released, value `0` means it is activated. Note the same inversion as in the write server.

        Be careful, this is not a feedback from a sensor mounted on the machine. But rather a feedback of the PLC saying *yes I sent your last command in the write server*. Therefore, this bit must never be trusted before writing a first time the corresponding bit of the write server.

    - Engine status

        Value `1` means the engine is ON, value `0` means the engine is OFF.

    - Operation mode

        Value `00` means **local** mode, Value `01` means **remote** mode,  Value `10` means **autonomous** mode, Value `11` means **emergency** mode.

- Register 2

    | Position | Name | Encoding | Description | Notes |
    | --- | ----------- | ----------- | ----------- | ----------- |
    | MSB | Error 2 | bits [7:4] : unused, bit [3] : Missing heartbeat, bit [2] : Shovel position, bit [1] : Baumer error, bit [0] : Emergency buttons 2 |  | see below |
    | LSB | Error 1 | bit [7] : Emergency buttons stop, bit [6] : ZoneSafe stop, bit [5] : Rear OS3 error, bit [4] : Front OS3 error, bit [3] : Rear OS3 warning field, bit [2] : Front OS3 warning field, bit [1] : Rear OS3 protective field, bit [0] : Front OS3 protective field |  | see below |


    - MSB bit [5] : Missing heartbeat

        Value `0` means that the heartbeat has not been updated since more than the allowed delay (300ms currently), value `1` means all good.

    - MSB bit [4] : Shovel position

        Value `0` means that the the boom and bucket are not in the position considered as *safe* to drive, value `1` means all good.

    - MSB bit [1] : Baumer error

        Value `0` means that the speed sensor Baumer detected an error in its configuration, power supply, ..., value `1` means all good.

    - MSB bit [0] : Emergency buttons slot 2

        Value `0` means that one of the buttons in the 2nd slot of emergency buttons is pressed, value `1` means all good.

    - LSB bit [7] : Emergency buttons slot 1

        Value `0` means that one of the buttons in the 1st slot of emergency buttons is pressed, value `1` means all good.

    - LSB bit [6] : ZoneSafe stop

        Value `0` means that the ZoneSafe device detected a tag in the field around the machine, value `1` means all good.

    - LSB bit [5] : Rear OS3 error

        Value `0` means that the rear safety lidar went in error mode, value `1` means all good.

    - LSB bit [4] : Front OS3 error

        Value `0` means that the front safety lidar went in error mode, value `1` means all good.

    - LSB bit [3] : Rear OS3 warning field

        Value `0` means that the rear safety lidar detected an object in its warning field, value `1` means all good.

    - LSB bit [2] : Front OS3 warning field

        Value `0` means that the front safety lidar detected an object in its warning field, value `1` means all good.

    - LSB bit [1] : Rear OS3 protective field

        Value `0` means that the rear safety lidar detected an object in its protective field, value `1` means all good.

    - LSB bit [0] : Front OS3 protective field

        Value `0` means that the front safety lidar detected an object in its protective field, value `1` means all good.

- Register 3

    | Position | Name | Encoding | Description | Notes |
    | --- | ----------- | ----------- | ----------- | ----------- |
    | MSB | Bell-crank angle | [0..255] is [0..100%] of the range of the bell-crank | It corresponds to a physical angle of [318°..251°]. | The maximum angle of the bell-crank is not reachable in each position of the boom, due to kinematics design. |
    | LSB | Boom angle | [0..255] is [0..100%] of the range of the boom | It corresponds to a physical angle of [-40..46]. |  |

- Register 4

    | Position | Name | Encoding | Description | Notes |
    | --- | ----------- | ----------- | ----------- | ----------- |
    | MSB |  |  |  |  |
    | LSB | Steering angle | [-128..127] is [-100%..100%] of the steering angle. Two’s complement encoded. | It corresponds to a physical angle of [-35°..35°]. | If it is negative, it means the vehicle turns to the left. |

- Register 5

    | Position | Name | Encoding | Description | Notes |
    | --- | ----------- | ----------- | ----------- | ----------- |
    | MSB | Heartbeat | Encoded as an Uint16 value | Written periodically by the PLC. To be checked by the user. |  |
    | LSB | Heartbeat |  |  |  |

- Register 6

    | Position | Name | Encoding | Description | Notes |
    | --- | ----------- | ----------- | ----------- | ----------- |
    | MSB | Boom lower pressure | [0..255] is [0..510 bars] | Pressure in the cylinder to lower the load. |  |
    | LSB | Boom lift pressure | [0..255] is [0..510 bars] | Pressure in the cylinder to lift the load. |  |

- Register 7

    | Position | Name | Encoding | Description | Notes |
    | --- | ----------- | ----------- | ----------- | ----------- |
    | MSB | Bucket dump pressure | [0..255] is [0..510 bars] | Pressure in the cylinder to dump the load. |  |
    | LSB | Bucket digg pressure | [0..255] is [0..510 bars] | Pressure in the cylinder to digg and grab the material. |  |

- Register 8

    | Position | Name | Encoding | Description | Notes |
    | --- | ----------- | ----------- | ----------- | ----------- |
    | MSB | Bucket lever | [-128..127] is [-1.0..1.0] | Position of the bucket lever in local mode |  |
    | LSB | Boom lever | [-128..127] is [-1.0..1.0] | Position of the boom lever in local mode |  |

- Register 9

    | Position | Name | Encoding | Description | Notes |
    | --- | ----------- | ----------- | ----------- | ----------- |
    | MSB | Brake pressure | [0..255] is [0.0..1.0] | Pressure of the brake pedal in local mode. |  |
    | LSB | Throttle pedal | [0..255] is [0.0..51 bars] | Position of the throttle pedal in local mode. |  |

## Hardware architecture

The hardware is defined by both the security and the functionalities. In order to make it as reliable as possible, we implemented two PLCs. One is responsible to manage the inputs from the safety sensors, while the other drives the vehicle. The two PLCs communicate thanks to wires, so that it works as long as it is wired, no matter the network. The PLC responsible to drive the car is connected to the machine interface that provides all sensors metrics, and the possibility to send commands for steering, brake and throttle.

The focus of this document is on the software library, thus the hardware architecture is not furthermore described.

## Software architecture

The code is written in Python and uses the following libraries : 
- PyModbus, for the Modbus communications in python
- Loguru, for the logs

Currently, we use `pymodbus==2.5.3` and `loguru==0.7.0`. At some point, we will need to updat pymodbus at least.

### Repository structure

For more information on how to install the library and basic start, read the `README.md` at the root of this repository.

#### Source files

For more clarity, the code is separated in subfolders : 
- `machine`

    It contains all the code to handle the vehicle, this is basically the entry point for any user that want to control it. No matter the protocol used to connect to the machine, it is hidden to the end user. It is kind of an abstraction layer of the protocol and lower level stuff.

- `hal`

    Low level access to the machine's hardware, it is the link to the PLC on the vehicle. The end user does not need this code. At this point and for this machine, we use a Modbus protocol implementation, but it could be *easily* replaced by any other protocol without the need to change the higher level Class and methods.

- `utility`

    It contains several useful classes, used anywhere in the repository.

#### Miscellaneous  files

All diagrams made to define the architecture and the repartition of the commands are stored in the folder `diagrams`.

The folder `doc` contains this report and testing reports, with the progress made over each test, as well as some information on the corrective actions.

Logging information can be found in the... `log` folder.

We have got a virtual environment setup, which can be started by running `conda activate pmi` or under windows, the file `env.bat`. For more information about it, refer to the `README.md`.

For more information about the quick deployment of this repository, the changelog, etc, we have a `README.md` as well. 

Last but not least, the `setup.py` allows us to distribute this repo in a system as a python package.

### Class diagram

#### Top level machine interface

#### ![](..\diagrams\class-diagram-remote-controller.svg)

<center>Simplified class diagram of the python machine interface</center>

The central class is `MachineDriver`. As mentioned earlier in this [section](#repository-structure), the several subfolder are represented by the folder icons. Only the *utility* subfolder is not shown here, as it is integrated close to the classes where used.

### Class description

In this section, we will dive in the classes and methods, with the focus of the interactions between the classes, to understand which classes is responsible for what. 

#### Utility classes

##### DataHandler and DataEvaluation

The main class here is `DataHandler` and uses `DataEvaluation` during its process. Our `DataHandler` is basically a code that handles changes in a specific data for us, and fires a callback pre-registered in case of changes. 

In order to allow more flexibility for the user, each `DataHandler` has a list of `DataEvaluation` for one specific data. It means that for one data, we can launch several callbacks depending on the changes on the data. What is the data ? The data can be anything, as long as we have a way of evaluating it. The evaluation can be made by any way, it simply must return a boolean that states whether a change happened or not. Also, the data is memorized by the `DataHandler`, and each time a new data is registered, it is updated.

The `DataEvaluation` contains a list of callbacks, and the specific evaluation method. If this method returns `True`, then each of the callbacks in the list are called with the actual data, and the memorized data of the `DataHandler`.

![DataHandler](..\diagrams\data-handler.svg)

<center><h6>DataHandler and DataEvaluation class diagrams</h6></center>

Let us discuss it in the next example :

```python

# unequal function evaluation
def evaluate_on_unequal(new_int, mem_int):
    return (new_int != mem_int)

# callback for the unequal function
def cb_on_unequal(new_int, mem_int):
    print('new_int on unequal: {}, mem_int : {}'.format(new_int, mem_int))

# smaller function evaluation
def evaluate_on_smaller(new_int, mem_int):
    return (new_int < mem_int)

# callback for the smaller function
def cb_on_smaller(new_int, mem_int):
    print('new_int on smaller: {}, mem_int : {}'.format(new_int, mem_int))

# bigger function evaluation
def evaluate_on_bigger(new_int, mem_int):
    return (new_int > mem_int)

# callback for the bigger function
def cb_on_bigger(new_int, mem_int):
    print('new_int on bigger: {}, mem_int : {}'.format(new_int, mem_int))

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

```

In this example, we set up a `DataHandler` to compare integers. The interesting point here is that we can handle changes with different callbacks, such as a smaller new integer triggers not only the smaller callback, but also the unequal callback. While this example is really basic, it makes sense with bigger data structures.

##### EdgeDetection

This class provides two methods, in order to detect changes in a signal : 

- `detect_edges_2pos(old, new)` : detect the rising and falling edges of two positions signals 
- `detect_edges_3pos(old, new)` : detect the rising and falling edges of three positions signals, for example the hats of the joysticks, with a range of [-1, 0, 1].

Constants are defined in the class : 
```python

RISING_EDGE_POS = 1     # from 0 to 1
FALLING_EDGE_POS = 2    # from 1 to 0
RISING_EDGE_NEG = -1    # from 0 to -1
FALLING_EDGE_NEG = -2   # from -1 to 0
NO_EDGE = 0

```

##### PeriodicTimer

This class is a child of `threading.Timer`, and allows us to have a periodically repeated timer. The interval is specified through the constructor. The method `kill()` allows us to stop the timer.

##### TimestampHandler

This class is used to store and get the timestamp of the latest valid Modbus transaction. It uses a mutex to protect the timestamp, since it is written from the main thread, but read from the thread of a `PeriodicTimer`. If you plan to use another mutex somewhere in the code, be aware of the deadlock problematic !

##### PMI_logger

For the logging, we use the module `loguru`, installed via pip. It can be configured in many ways, and offers several handlers, such as terminal and logfile. In order to configure the logging operations, we use the class `PMI_log_initializer` :

- level of logging in the terminal
- level of logging in the logfile
- path of the logfile

```python
PMI_logger(
    terminal_lvl="INFO", 
    logfile_lvl="DEBUG", 
    logfile_path='../../../log/log.txt'
)
```

A call of the constructor is enough to configure the whole logging operations of the project.

#### Machine

##### MachineLogic

This class is a representation of the machine mechanisms. For example, if we get 5 times the command to increase the gear speed but only have a 4 gear speeds gearbox, we will have a problem. So this class makes sure that the mechanical limitations of the machine are respected before being sent to the `MachineDriver`. Also, it keeps track of the state of the machine in the time. 

In the future, it could also help and prevent random stupid actions like putting reverse when the machine is going full speed forward. But this is currently not implemented.

##### MachineDriver

`MachineDriver`offers quite a high level interface to the machine, it makes abstraction of the low level protocol used, and provides most of the information to the user through callbacks. These callbacks must be registered in the user's code.

The class can be configured in 3 ways, thanks to its constructor :
1. bidirectional : it has access to both Modbus servers
2. unidirectional read : it has only access to the RR server
3. unidirectional write : it has only access to the WR server

To be able to configure it, use the parameters `reader` and `writer` in the constructor :
```python
machine = MachineDriver(ip_address='localhost', port_sender=1502, port_receiver=1503, reader=True, writer=True)
```

The reason for this choice, is that in ROS2 we needed to separate the writing from the reading in two differents nodes. 

The class contains two `DataHandler` : 

- one to handle the reading of the read registers
- one to handle the reading of the write registers

Currently, the evaluation methods are firing no matter whether the data is different or not. But it can be easily changed by implementing a different evaluation method.

It also has two `PeriodicTimer` : 

- one to read either the RR server or WR server, or both.
- one to check the latest valid timestamp of a Modbus transaction

With the callbacks registered by the user, data will be sent to the user. The advantage of using user callbacks is that we use the same code for several use cases : 

- monitoring of the machine information
- taking decisions to drive the machine
- sending the machine information to a display
- ...

Also, the user should increment the heartbeat of the machine, thanks to the method `increase_hearbeat()`. It can be done from anywhere, but must the frequency must be higher than the period of the heartbeat check in the PLC (currently 300 ms).

Once the machine is connected, and the periodic reading started thanks to the method `start(...)`, each of the read request provided by the `ModbusManager(...)` contains two things, packed as a Tuple : 

1. either response or error code
2. timestamp or None

For the exact definition of the error codes, see [below](#modbusmanager) the explanation of the class `ModbusManager`. When receiving a response, the `DataHandler` are updated and the callbacks fired if necessarily. On the other side, if we receive an error code, the method `__handle_disconnection()` is called. It does a few actions : 

1. disconnects totally the machine thanks to `ModbusManager.get_instance.disconnect()`, which makes sure both clients are totally closed.
2. kills the `PeriodicTimer` in order to stop requests during the disconnection.
3. initiates a connection procedure again.  
4. restart `PeriodicTimer` once the connection is established again.

##### MachineWrite

This class is used to transmit commands to the machine. The user should always use this class and not `HAL_Write` or `MachineLogic` or anything else. It is not a hazard that `MachineDriver.set_all()` takes a `MachineWrite` object as parameter. The any other possibility is to call `MachineDriver.operate_with_logic()` that takes a `MachineLogic` object as parameter, but don’t be fooled, a conversion to `MachineWrite` is made behind with a call to `set_all()`. 

It is an abstraction to the low level values. For example, in the Modbus server, the 4th speed is `0x08`. But in the machine level, we use `GS_4TH = 4`. It will be translated later to the correct Modbus value. You can find more about the reasons we use it in [this section](#level-conversions).

##### MachineRead

Same goes to `MachineRead`. It is obtained by converting a `HAL_Read` object using the right method. It also provides information from the machine but converted to a more convenient form.

#### HAL

##### ModbusManager

One more step closer to the hardware is the class `ModbusManager`. This class is responsible for all transactions with the two Modbus servers : 

- connections and disconnections
- writing requests
- reading requests

With two servers come two clients. The class has up to two instances of `pymodbus.client.sync.ModbusTcpClient ` : 

1. *sender* refers to all communications of commands to the machine
2. *receiver* refers to all communications of information from the machine

It is fixed by the same parameters in its constructor than for the class `MachineDriver`: 

```python
self.modbus_manager = ModbusManager(self.reader, self.writer)
```

Once the connection to the two servers is established, it is maintained throughout all the program's execution, unless an error occurs. We have got two main functions, both private, that allows the writing and reading of the registers. Also, they deal with errors that could happen during a transaction : 

- `__write_registers(self, address, values)`
- `__read_registers(self, address, count, read_wr=False)`

These are the two entry points to the Modbus servers. As they are private, they may only be used from this class. Therefore, several more methods are implemented, based on these two methods : 

- `write_machine(self, machine_write)`
- `write_heartbeat(self, hr)`
- `read_machine_rr(self)`
- `read_machine_wr(self)`

We decided that we will write all the registers simultaneously, for these reasons : 

1. the payload is relatively small, it should not cause any trouble with the bandwidth
2. most of the registers have several features encoded 
3. it makes sense to keep all the commands to the vehicle closely related, 
to maintain a strong coherence

The only exception is for the heartbeat register. It needs to be written at an accurate frequency, and cannot wait for a new input to decide a new command.

Regarding to the read methods, we have got either the "read registers", aka RR server, or the "write registers", aka WR server. We may want to read both in order to check and back up what we are writing. 

The two base methods deal the errors. Basically, 4 return codes are defined : 

- 0 in case of success
- 1 in case of the sender client got disconnected
- 2 in case of the receiver client got disconnected
- 3 for any other error

As mentioned earlier, these codes are transmitted to the higher level class `MachineDriver`, which will handle the processes of reconnection. It is important that it is handled from a higher level so that the requests stop arriving to the low level layer.

##### HAL_Write

When on a higher level a call to `MachineDriver.set_all(machine_write)` is made, the object is converted to a `HAL_Write` object. The abstraction is lost at this level, since we’re close to the hardware. The high level information are converted to encoded bytes, which will be written in the registers, following the protocol describer [here above](#protocol-description).

##### HAL_Read

The bytes read from the Modbus registers are converted into a `HAL_Read` object, which will later be converted into a `MachineRead` object. The two steps allow abstraction toward the machine level.

### Tips and tricks 

#### MachineDriver set_machine_motionless

When calling the `MachineDriver.start()` method, you can add an optional parameter, called `set_machine_motionless` that is a boolean. If set to true, it will send a first command to the machine to ensure that the machine does not move.

#### ModbusManager timeout

When calling the `ModbusManager.get_instance().connect()` you can add an optional parameter, called `timeout` that sets the timeout of the PyModbus clients to the desired value. However, depending on the value, the PLC’s server refuse the connection… To be investigated !

### Data flow

In this section we try to explain how the code is running. In the case of a *remote controller*, we have basically two main tasks : 

1. polling of the inputs and sending commands to the machine
2. polling of the machine’s register and updating the `Controller` with fresh data

We could add two minor tasks, but that are important, safety wise : 

1. heartbeat PC update
2. timestamp comparison

The polling of the machine’s register is quite a lonely task. Once `MachineDriver` is started, the periodic timer is started, and at each timeout, the polling is done, in a separated thread. The new data are sent to the registered callbacks of the `DataHandler`.

![](..\diagrams\sequence-read.svg)

<center><h6>Polling the machine’s registers</h6></center>

To write, it is simpler. A `MachineWrite` is converted to a `HAL_Write` object, and sent to the `ModbusManager`, which will encode it in the registers.

A call to `MachineDriver.increase_heartbeat(...)` is needed to update the heartbeat. This must be done at least faster than each 300ms, and as close as possible to the code that uses `MachineDriver.set_all(...)` as we want it to fail simultaneously as the code if something should happen.

Regarding to the timestamp check, basically we check it with a separated timer. At each timeout we check if the latest valid timestamp is still not too old. This can help to detect network failures or too big latency. So far, it is not totally implemented, only an error is logged from the dedicated callback. 

### Level conversions

In this project, we defined 2 levels :

- `hal`
- `machine`

We need these levels in order to uncouple the functionalities and make sure that the code will be easier to maintain. For example, if we want to change the Modbus protocol to any other protocol, we only need to write the `hal` module again, and only partially. Let us take the example of the variable shift mode. The binary encoding defined by the protocol for our Modbus server is :

- `00` is for automatic low
- `01` is for manual
- `10` is for automatic high

This is at a very low level. We could use these binary values as well in higher levels, but first of all it doesn't say much to the final user what `00` is for, and secondly, if we ever change the values or the protocol, then we need to write all levels again. That is why we use conversions between the levels. If we continue with shift mode, in the machine level, its values are : 

- `0` is for automatic low
- `1` is for manual
- `2` is for automatic high

Now you will tell me, what is the difference between binary and decimal ? Well, of course it doesn't change to use a binary or decimal, but the thing is : no matter the value used in the lowest level, in the machine level it will always be the same. It makes it easier to maintain the code if you can change the low level protocols and values, but you don`t need to update the user code. If we had a GUI level, we could use String to represent the values. We would like to have a clear and human readable description of the shift mode : 

- `low` is for automatic low
- `manual` is for manual
- `high` is for automatic high

Another non negligible advantage is the abstraction provided by this method. Let us take the parking brake as an example. It is encoded on the Modbus server on one bit : 

- `0` for activated
- `1` for released

It is quick to notice the logical inversion done here. 0 usually means off, while 1 means on. In this case and for security reasons, it is better to have a 0 for activated. If we don’t use conversions, then in the machine level we need to send a False to activate the brakes, sounds strange, no ? But if we define a constant `ACTIVATE_BRAKE = False`, and we keep using it in the machine level, the abstraction keeps us safe and confident.

Of course we need an easy and fast way to make the conversion. Let us start with the lowest class for a read operation, the class `Hal_Read`. When we make a read request via the `ModbusManager`, we receive an array of Uint16. This array is decoded and each field gets its value. These value are still binary encoded. To get a decimal value that is already easier to read, we call the method `MachineRead.import_from_hal_read(...)`. It will create a `MachineRead` object with the decoded values. For example, instead of having the speed encoded from 0 to 255 on a Uint8, we now have the speed encoded in a Float from 0 to 51 km/h. Same for the other values. 

Let us see the reverse way, or better said the way to make a write request. We start with a `MachineLogic` object, that is kind of an abstraction of the machine. Basically, it deals all the changes that are possible in the vehicle, such as the gearbox, shift mode, ... It is updated via a controller at higher level, and then converted to a `MachineWrite`, via its method `MachineLogic.to_machine_write()`. When we then call the method `MachineDriver.set_all(machine_write)`, it is converted to an object of the class `HalWrite` thanks to the method `HalWrite.import_from_machine_write(...)`.

It is important to use the right class at the right level. Users of this library should always care about `MachineWrite` and `MachineRead`. All the constants are defined in this class, and it they are not used, errors will be thrown. 
