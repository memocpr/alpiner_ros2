# Python Machine Interface PMI

This package provides a python machine interface for the projet AT-COM.

## Related documentation

1. More in depth documentation of [this repository](https://github.com/syrto-AG/P12-python-machine-interface/blob/master/doc/report.md).
2. `README.md` from the [`P12-ros-bridge-2-machine`](https://github.com/syrto-AG/P12-ros-bridge-2-machine/blob/main/README.md).
3. Main documentation of the project, available [here](https://github.com/syrto-AG/P12-documentation/blob/master/src/resources/software/ros/overview.rst#bridge-towards-modbus)

## Installation

1. Clone the repository : `git clone git@github.com:syrto-AG/P12-python-machine-interface.git`
3. Move into the repository : `cd P12-python_machine_interface`
2. Select the branch corresponding to what you want to do (check here below for branch options)
4. Create the virtual environment with Conda : `conda env create -f env.yml`
5. Activate the virtual environment : `conda activate pmi`
6. Install the package : `pip install -e .`
7. Verify it is installed by running : `pip list | grep -i pmi` and you should see a line with a package called **pmi**, currently in version *1.0.0*
8. In a new folder, clone this repository : `git clone git@github.com:syrto-AG/P12-wheel-loader-linkage-geometry.git`
9. Install it in your `pmi` environment
10. Voilà !

## Branches

| Branch   | Purpose |
|-----------|----------|
| **master** | **Release branch** — stable, production-ready version used for demos, customers, and investors. The latest commit must always work. |
| **testing** | **Staging branch** — internal testing version. Deployed on the test machine. Should generally run, but may contain unspotted bugs. |
| **dev** | **Development branch** — used daily at the office or on-site for small commits and active development. May include broken or unfinished work. |

- Merging from *dev* to *testing* : normal merge, no squash.
- Merging from *testing* to *master* : merge with squash : `git merge --squash testing` and `git commit -m "Merged testing into master"`. Tags if needed to keep track of compatibilities accross all ROS2 nodes and system.

## Example

To get an example, have a look at the package [P12-ros-bridge-2-machine:bridge_read.py](https://github.com/syrto-AG/P12-ros-bridge-2-machine/blob/main/src/ros2machine/ros2machine/bridge_read_machine.py) for a read implementation, and [P12-ros-bridge-2-machine:bridge_write.py](https://github.com/syrto-AG/P12-ros-bridge-2-machine/blob/main/src/ros2machine/ros2machine/bridge_write_machine.py).

## Testing with Modbus

In order to run this script, make sure you have a Modbus server running on your machine. Two test servers are available in `src/pmi/tests/`. Run each one in a dedicated terminal and set up parameters of the `MachineDriver` according to your configuration.

## Logging

The *loguru* module from Python is used. A class named *PMI_logger* takes care of setting up the log operations. Through its constructor, one can define the log level of both the logfile but also of the terminal, and the path to the logfile. Once called, no further actions are required. Simply use `logger.<...>` in any other file. 

```python
from pmi.utility.atcom_logging import PMI_logger

if __name__ == '__main__':

    # setup logger
    PMI_logger(
        terminal_lvl='INFO', 
        logfile_lvl='DEBUG', 
        logfile_path='log.txt'
    )
```

## Changelog

Here you can find the most impacting changes to the library. Only changes that could affect implementations using this library are mentioned here.

- from commit **[f68e4bbdb719778f8f1ce950400c128a80c5cf7f](https://github.com/syrto-AG/P12-python-machine-interface/commit/f68e4bbdb719778f8f1ce950400c128a80c5cf7f)**, some fields of `MachineReadOthers` have been removed because they were either duplicated or deprecated:

    - Pedestrian
    - Shovel safe
    - Emergency stop

- from commit **[d082687a21cbf0e1c2f5e58bb0a06d495bef085c](https://github.com/syrto-AG/P12-python-machine-interface/commit/d082687a21cbf0e1c2f5e58bb0a06d495bef085c)**, `MachineReadErrors` is fully implemented and functional, meaning that we have got the errors from the lowest level security layer transmitted to the Machine's world, and therefore one layer higher to the ROS users.
  
- from commit **[e46223eeb4bedf6e2b98d7164634f8f6a0d9045b](https://github.com/syrto-AG/P12-python-machine-interface/commit/e46223eeb4bedf6e2b98d7164634f8f6a0d9045b)**, the class ModbusManager is not a singleton anymore. It was modified in order to make it possible to have two implementations of MachineDriver running concurrently, so that we can have two separated bridges : one for reading, one for writing. The main goal is to increase the global performance of the reading. Therefore, both MachineDriver and ModbusManager take a parameter *reader* and *writer* to specify if they are reading or writing the machine. They can also be both. 

- from commit **[028eca94158eccbeb7b3ceaef86fca07c335c981](https://github.com/syrto-AG/P12-python-machine-interface/commit/028eca94158eccbeb7b3ceaef86fca07c335c981)**, the bit 4 in the LSB register 1 of the write server is now used to disable the front lidar, when the teleoperator wants to do a loading operation. 

- from commit **[d85186b4a2ed137bf7921f7244649996ab5f3408](https://github.com/syrto-AG/P12-python-machine-interface/commit/d85186b4a2ed137bf7921f7244649996ab5f3408)**, the constants *DM_FORWARD*, *DM_REVERSE* and *DM_NEUTRAL* in the class **MachineRead** have the same values than in the class **MachineWrite**, for consistency. 

- from commit **[ff9f9a2bd62ce9eaebc12198e3516efcdf0cae81](https://github.com/syrto-AG/P12-python-machine-interface/commit/ff9f9a2bd62ce9eaebc12198e3516efcdf0cae81)**, the callback for the unchanged timestamp is called everytime, but with an additional flag to indicate whether the timestamp is behaving correctly or not. 

- from commit **[db2e7cdf8175290705816a3ab0fa19e8da2da38b](https://github.com/syrto-AG/P12-python-machine-interface/commit/db2e7cdf8175290705816a3ab0fa19e8da2da38b)** the remote-controller is part of another repository. This changes is needed in order to keep only the needed source code on the embedded computer on the machine, which is headless and therefore shouldn't have to deal with GUI and Cameras.

- from commit **[212f24f3483aa9d01d6bb5327057aa6ab6de4a8a](https://github.com/syrto-AG/P12-python-machine-interface/commit/212f24f3483aa9d01d6bb5327057aa6ab6de4a8a)**,
we defined in each world (hal, machine, remote) constants that must be used exclusively in their respective world. We also wrote conversions methods from one world to another. Make sure to always use the right constants in the right world ! You can find more doc about it in the main doc.

- from commit **[83bce095dfb24abaecd960c30fe138e3a17702de](https://github.com/syrto-AG/P12-python-machine-interface/commit/83bce095dfb24abaecd960c30fe138e3a17702de)**,
we use the library *loguru* and not *logging* anymore, because it works much better with ROS. Also, the file `utility/atcom_logging.py` contains the new class for logging : `PMI_logger`.

- from commit **[5b86ea06f5824b4c0f28e58e7d187f5fa2be9351](https://github.com/syrto-AG/P12-python-machine-interface/commit/5b86ea06f5824b4c0f28e58e7d187f5fa2be9351)**,
you can set an option to the method `MachineDriver.start(set_machine_motionless=True)` in order to initialize the registers of the write server with known values. These values make sure the machine is in a known state, and that it won't move.

- from commit **[2ee4e704cbf81d8efa6e7f837df09ea35ce0b9f0](https://github.com/syrto-AG/P12-python-machine-interface/commit/2ee4e704cbf81d8efa6e7f837df09ea35ce0b9f0)**,
heartbeat does not belong to `MachineWrite` anymore. The reason is that we write it periodically from another thread.

- from commit **[3c80fa98acc167da6d75dbfce695d12a02df13da](https://github.com/syrto-AG/P12-python-machine-interface/commit/3c80fa98acc167da6d75dbfce695d12a02df13da)**,
in the class `ModbusManager`, the method `read_machine(...)` is now called `read_machine_rr(...)` and the method `read_machine_commands(...)` is now called `read_machine_wr(...)`, for a better match with the names in the class `MachineDriver`.

- from commit **[568a12748c318e7c84c583d56532f9db2ac95570](https://github.com/syrto-AG/P12-python-machine-interface/commit/568a12748c318e7c84c583d56532f9db2ac95570)**,
the file `edges.py` contains a class name `EdgeDetection` with the constants defined inside the class, for more clarity.

- from commit **[bb58289e78090a09c93dc83e97db4b71298d52ac](https://github.com/syrto-AG/P12-python-machine-interface/commit/bb58289e78090a09c93dc83e97db4b71298d52ac)**,
methods from the class `ModbusManager` return error codes defined in the same class :

    * SUCCESS = 0
    * ERROR_SENDER_DISCONNECTED = 1 in case of the client connected to the write server is not connected anymore
    * ERROR_RECEIVER_DISCONNECTED = 2 in case of the client connected to the read server is not connected anymore
    * ERROR_REQUEST_FAILED = 3 for any other error

    Therefore, the method `write_machine` of the class `ModbusManager` returns one of these error codes, as an Integer.

    For the methods `read_machine_rr` and `read_machine_wr` of the same class, they return a Tuple containing either a valid value data and timestamp, or one of these error codes and a None.

    Of course, these changes are repercuted in the class `MachineDriver`, especially in the method `set_all` and `read_all`. They are mainly used by the method `__run` in order to deal with client disconnections.

- from commit **[24c76023e151e29b48026f8d7c480ed793865459](https://github.com/syrto-AG/P12-python-machine-interface/commit/24c76023e151e29b48026f8d7c480ed793865459)**, 
the class `DataEvaluation` takes a list of callback functions, rather than a single function. Therefore, when registrating a `DataEvaluation` to a `DataHandler`, a List is required : 

    ```python
    handler = DataHandler()
    handler.register_evaluation(callbacks=[cb_on_unequal], eval_func=evaluate_on_unequal, name='[UNEQUAL]')
    handler.register_evaluation(callbacks=[cb_on_smaller, cb_on_unequal], eval_func=evaluate_on_smaller, name='[SMALLER, UNEQUAL]')
    ```
    
    Thus, the method `init(...)` from the class `MachineDriver` takes a list of callback functions.

- from commit **[d88ca33cf2f1d291e8f52c0b92db78a1b958819d](https://github.com/syrto-AG/P12-python-machine-interface/commit/d88ca33cf2f1d291e8f52c0b92db78a1b958819d)**, the attribute `gear_speed` of the class `MachineRead` is 1, 2, 3 or 4, rather than 0b0XXXX000.

- from commit **[5aec4fff7a1ff5f6a7aaa71522c8b1819a0cbc4b](https://github.com/syrto-AG/P12-python-machine-interface/commit/5aec4fff7a1ff5f6a7aaa71522c8b1819a0cbc4b)** the class `Controller` is not a singleton anymore. Since it needs to be specific to an IP address and ports (it contains a `MachineDriver` objects), it doesn't make any sense to make it a singleton.

- from commit **[07be14c35947565e226b0012453f9a2b435143b0](https://github.com/syrto-AG/P12-python-machine-interface/commit/07be14c35947565e226b0012453f9a2b435143b0)** the class `Machine` becomes `MachineDriver` to better match with the naming of the class `MachineLogic`. Basically, `MachineDriver` is responsible to deliver read/write requests from/to the HAL and the Modbus server, while the class `MachineLogic` deals with the gear shifting, directional modes, toggling of options, ... 

- from commit **[139939143dcbb02639e7a4861b98caae5e8bc9b2](https://github.com/syrto-AG/P12-python-machine-interface/commit/139939143dcbb02639e7a4861b98caae5e8bc9b2)** the callback of the `DataHandler` and `DataEvaluation` takes two arguments : 
    
    1. data : the new data

    2. mem_data : the memorized data

    It means that the callback defined by any code using the class `MachineDriver` must be updated with a second argument.



