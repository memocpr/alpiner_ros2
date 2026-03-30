# State after test on site 16.08.2022

This was the first test on site with the new python machine interface.
The machine stayed on place, because the quality of the connection quickly dropped as soon as we went further.

## Network

The connection with the wheel loader is very unstable.
If the vehicle is parked near an access point, the quality is acceptable, with a ping time around 15ms.
However, as soon as we drove it further, it quickly got disconnected. 
Also, we have from time to time a ping time of more than 1000ms, and even some timeouts...
Solutions :

- improve antena on top of the wheel loader (with a phone, we can get wifi until much further)
- change to a 5G receiver ? https://new.siemens.com/global/en/products/automation/industrial-communication/industrial-5g/5g-router-scalance-mum.html

## Writing procedure

-  some weird behaviour with the initialization of the pedals : full gaz and full brake
   -  corrected with commit **[bc27765631bbbab8712510e50875f54512cf79eecommit ](https://gitlab.hevs.ch/SPL/syrto/AT-Com/python_machine_interface/-/commit/bc27765631bbbab8712510e50875f54512cf79ee)**, quite a dirty fix but necessary because of Pygame…
- parking brake is not working
- forward/reverse ok
- lights ok
- horn ok
- gear speed unknown if working
-  steering, boom and bucket has a strange sensivity -> joystick refresh rate ?
   - corrected with commit **[e4cfd1df1941b7219d1ba4d5c1aaa9a5c64e02b0](https://gitlab.hevs.ch/SPL/syrto/AT-Com/python_machine_interface/-/commit/e4cfd1df1941b7219d1ba4d5c1aaa9a5c64e02b0)**
- steering : direction inverted
- autodig ok
- ecss, kickdown, shifthold, tm cutoff not verified on site

## Reading procedure

- speed seem to be ok until at least 5km/h (could not test it more)
- boom, bucket and steering have consistent values, but weirdly scaled
- gear speed is not working
- directional mode is not working
- fuel level ok at this time at least
- operation mode, engine status, and emergency look ok, but could not control it in their other states
- shovel position to be tested 
- parking brake : reading seem to be ok, at least it is toggled by the button

# TODOs with Lukas next time

1. check functionalities of register 1 MSB : kickdown, autodig, t/m cutoff, shifthold switch, ecss and parking brake : toggle, single push, maintained, …
2. clarify the read of bucket, boom, speed, and some other options
3. install the 3 positions button + encode it in registers
4. temporized shutdown

# State after test on site 23.09.2022

## To improve/do/clarify

- timeout on modbus client is not working -> maybe increase it ?
- change shifthold to "as long as maintained", change kickdown to "as long as maintained"
   - corrected in commit **[0abccc9eb1662f67de495b32ff028aaa3ce06f37](https://gitlab.hevs.ch/SPL/syrto/AT-Com/python_machine_interface/-/commit/0abccc9eb1662f67de495b32ff028aaa3ce06f37)**
- change shiftmode according to Lukas : 00 is low, 01 is manual, 10 is high, 11 is undefined (probably interpreted as manual, TBC)
   - corrected in commit **[8eefa637ae87bc1e86854c507b9d4bc76aec6536](https://gitlab.hevs.ch/SPL/syrto/AT-Com/python_machine_interface/-/commit/8eefa637ae87bc1e86854c507b9d4bc76aec6536)**
- temporized shutdown to be defined more precisely
- maybe change quadratic to linear again for joysticks ?
   - corrected in commit **[fdfa968705eece89f0d40d79bf30502d35878241](https://gitlab.hevs.ch/SPL/syrto/AT-Com/python_machine_interface/-/commit/fdfa968705eece89f0d40d79bf30502d35878241)**
- change hearbeat to user, and not to driver
   - implemented in commit **[03950bde81d0c07060c2b3d9619d904d2b879b9c](https://gitlab.hevs.ch/SPL/syrto/AT-Com/python_machine_interface/-/commit/03950bde81d0c07060c2b3d9619d904d2b879b9c)**
- identify left and right joysticks
   - implemented in commit **[cb526960814b1863648e5590256fa77645c2f6e7](https://gitlab.hevs.ch/SPL/syrto/AT-Com/python_machine_interface/-/commit/cb526960814b1863648e5590256fa77645c2f6e7)**
- documentation and diagrams

## Reading procedure

- speed is tested and ok until at least 6km/h. it is always positive, must be combined with directional mode to determine the direction
- fuel level ok, but is moving a lot, since it is the raw value of the sensor, which is impacted by the movements of the fuel in the tank when driving
- others bytes : all ok (emergency == 1 not tested though, the signal would come from the safety sps)
parking brake is special : there is no feedback from the machine, it is only a feedback of the sps that says "ok I activated/released the brake as you asked me". operation mode to be tested once we get the new button
- error 1 and 2 : not tested nor used
- boom, bucket and steering : tested and works as expected. ranges are ok. when turning to the right, the value is negative. 
- heartbeat : no increment from the side of lukas
- all 4 remaining pressure sensors to be tested

## Writing procedure

- gear speed ok on our side, the registers are updated, however a conflict exist in manual mode, depending on the electrical buttons
- active manual and low/high to be modified following lukas's explanations
- fw/rev/neutral works
- options : parking brake, ecss, shift hold, lights, horn, autodig, kickdown, t/m cutoff all works in the registers, but not possible to test them all in reality
- throttle and brake : works
- boom, bucket, steering : works
- heartbeat : maybe to fast, but works

# State after test on site 03.10.2022

## To improve/do/clarify

- brake pedal is way too abrupt -> find a mathematical function to reduce effectiveness at the beginning and increase later ?
- boom and bucket are not working anymore ??? probably linked either to the 3 new sensors implemented by Lukas, or by the operation mode that is not completed yet
- parking brake seems not to be working ?

# State after test on site 13.10.2022

## improved

- brake and gas pedal error is corrected
- parking brake problem is identified and can be solved by a procedure : always let the parking brake switch activated in the cabin
- boom and bucket must be cleared by a flag when the *remote* mode is turned on
- right is positive, left is negative

## To improve/clarify

- change pedals for a model with feedback 
- improve connectivity


