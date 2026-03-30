# Ros2 LL controller

This python package is dedicated to the AT-Com project. It translates a *geometry_msgs/Twist* into commands for the wheel loader, aka a MachineSetAll message. 

## Installation

```
git clone git@github.com:syrto-AG/P12-ros-nav-machine-controller.git
source_ros
cbp ros_ll_controller_python
```

Make sure that the package [atcom_msg](https://github.com/syrto-AG/P12-ros-msg) is installed and built in your ros2 workspace.

Make sure that the package [P12-python-machine-interface](https://github.com/syrto-AG/P12-python-machine-interface) is installed in the python environment you are using for your ros2 nodes.

## Launch

You can find the launch file in the `launch` folder of the package. In this launch file, you can tune different parameters of the LL controller. At the moment, you should care abotu the following parameters:

- p_gain_braking_ll_controller: proportional gain for the braking controller, range 0..1
- factor_throttle_reduction_when_not_active_braking: factor to reduce the throttle when a small deceleration is needed, range 0..1
- p_gain_linear_speed_ll_controller: proportional gain for the linear speed controller, range 0.05..2.0 (to be tested for each application)
- p_gain_angular_speed_ll_controller: proportional gain for the angular speed controller, range 0.05..2.0 (to be tested for each application)
- min_target_angular_speed_ll_controller: minimum target angular speed to consider doing the regulation, in rad/s

All the other parameters are not implemented yet.

You can launch the controller with the following command: `ros2 launch ros_ll_controller_python ll_controller.launch.py`.

## How does it work ?

### Sequence

This node works mainly on two types of events:

1. Reception of a new target velocity (geometry_msgs/Twist) on the topic `/cmd_vel_out` and MachineIndAll received on the topic `/atcom_wa380/wheeler/read/all`
2. A timeout of the command timer, that currently runs at 25Hz (to be increased at 50Hz, or same as the one from remote control)

At the reception of either message, the message's data is simply stored. 

When the command timer times out, the node computes the required commands to send to the machine, based on the last received target velocity and the last received MachineIndAll. 

### Regulator algorithm

Below is described the full sequence of operations performed at each command timer timeout:

![on_timeout](doc/ros_ll_controller_timeout.svg)

Below is described what happens when a change to idle is done :
![on_idle](doc/ros_ll_controller_idle.svg)

Below is described what happens when an acceleration is requested : 
![on_acceleration](doc/ros_ll_controller_accdec.svg)

### Results export

The output of this node is published on the topic `/atcom_wa380/wheeler/write/nav_ctrl` as a MachineSetAll message.

Please note that for this output to be taken into account by the machine, the [ros2machine:bridge_write](https://github.com/syrto-AG/P12-ros-bridge-2-machine) must be in ST_NAV_CTRL mode. Otherwise, the commands will be discarded.

Simultaneously, the node publishes the heartbeat for navigation on the topic `/atcom_wa380/wheeler/write/nav_heartbeat` as a Uint16 message.

### Cusp detection

A cusp is typically a point when the machine will change its direction, from forward to backward or vice versa. From the node [nav2_controller](https://github.com/syrto-AG/P12-custom-nav2-stack), we get a distance to the next cusp in meters. This value is encoded in a `geometry_msgs/Twist` message, in the `angular.x`field, as mentioned here : [geometry_msgs/Twist reviewed](https://github.com/syrto-AG/P12-documentation/blob/master/src/resources/software/ros/packages/navigation/nav2_reg_pp_controller.rst). Why do we do it like this ? Simply because it would have been to much work to change all the interface with a custom message... To be improved in the future.

#### Inputs and Conventions

- **`distance_to_next_cusp`**
  - `>= 0`: valid distance
  - `-1.0` (`DEFAULT_VALUE`): no measurement / unknown

- **`lin_speed`**: robot linear velocity  
- **`dt`**: time step since last update

**Key thresholds:**

- `DIST_MIN_AT_CUSP = 1.0` → declared *at the cusp*
- `DIST_MIN_ARRIVING_TO_NEW_CUSP = 2.0` → eligible to enter "arriving" mode
- `DIST_FROM_LAST_CUSP_TO_RESTART = 3.0` → distance required before detecting a new cusp
- `MAX_CNT_FURTHER_DISTANCE_TO_CUSP = 3` → tolerated increases while arriving
- `TIME_MIN_AT_CUSP = 2.0` → time the robot must stay at a cusp

---

#### Internal State Variables

- `currently_at_cusp`  
- `arriving_at_cusp`  
- `possible_to_detect_next_cusp`  
- `mem_distance_to_next_cusp`  
- `distance_from_last_cusp`  
- `cnt_further_distance_to_next_cusp`  
- `tm_beginning_at_cusp`  

---

#### State Flow Overview

##### 1. Already at a cusp (`currently_at_cusp == True`)
- A timestamp is maintained from first detection.
- Once `TIME_MIN_AT_CUSP` is exceeded:
  - `currently_at_cusp` resets to `False`
  - Robot is allowed to move again
- Detection of *next* cusp remains blocked by `possible_to_detect_next_cusp`.

##### 2. After a cusp (detection blocked)
If `possible_to_detect_next_cusp == False`:
- The robot accumulates travelled distance via `lin_speed * dt`.
- When `distance_from_last_cusp >= DIST_FROM_LAST_CUSP_TO_RESTART`:
  - All flags are reset
  - Detection becomes allowed again
- Otherwise, early return.

This prevents re-detecting the same cusp while still nearby.

---

#### 3. Approaching a cusp (`arriving_at_cusp == True`)

Cases:

1. **Distance measurement disappears but was previously known**  
   → Interpret as having reached the cusp.  
   → Call `set_values_when_cusp_detected()`.

2. **Both current and memorized distances are known**  
   - `_check_arriving_conditions()` evaluates whether distance is decreasing  
     or whether too many increases occurred.
   - Memory is updated.

3. **Otherwise** → insufficient data → no state change.

---

#### 4. Normal Mode (initial or idle state)

- If both current and memorized distances are unknown → do nothing.
- If memory is unknown but measurement is valid → initialize memory.
- If measurement is unknown but memory is valid → reset memory.
- If both are valid:
  - `_check_arriving_conditions()` determines whether to enter arriving mode.
  - Memory is updated.

---

#### Arriving Condition Evaluation (`_check_arriving_conditions`)

1. **Immediate cusp detection**  
   If `distance_to_next_cusp < DIST_MIN_AT_CUSP`:  
   → Cusp detected → `set_values_when_cusp_detected()`.

2. **If already arriving**  
   - Distance decreasing → continue arriving, reset error counter.  
   - Distance increasing:
     - Increment counter.
     - If it reaches `MAX_CNT_FURTHER_DISTANCE_TO_CUSP`:
       → Cancel arriving mode.
     - Otherwise tolerate the increase.

3. **If not yet arriving**
   - Enter arriving mode when distance is:
     - Decreasing relative to memorized distance **and**
     - Below `DIST_MIN_ARRIVING_TO_NEW_CUSP`.

---

#### When a Cusp Is Confirmed (`set_values_when_cusp_detected`)

- `currently_at_cusp = True`
- `possible_to_detect_next_cusp = False`
- `arriving_at_cusp = False`
- `cnt_further_distance_to_next_cusp = 0`
- `distance_from_last_cusp = 0.0`
- `mem_distance_to_next_cusp = DEFAULT_VALUE`
- Timestamp recorded for `TIME_MIN_AT_CUSP` handling

This starts a “cusp episode”:
1. Robot stays at cusp for at least `TIME_MIN_AT_CUSP`.  
2. Robot must travel `DIST_FROM_LAST_CUSP_TO_RESTART` before next detection.  

### Curvature to steering angle conversion

We use the method [compute_target_steering_angle() from ](https://github.com/syrto-AG/P12-python-machine-interface/tree/master/src/pmi/machine). This method is based on the work documented here : [Steering angle given turning radius](https://github.com/syrto-AG/P12-documentation/blob/master/src/domains/navigation/simple-kinematics.rst#steering-angle-to-achieve-given-turning-radius).

Computes the steering angle from the curvature contained in `cmd_vel.angular.y`.

1. Compute a safe turning radius (avoid division by zero):

```
radius = 1000.0 if cmd_vel.angular.y == 0.0 else 1.0 / cmd_vel.angular.y
```

2. Apply the steering geometry formula (L = wheelbase):

$$
\theta = \arccos\left( \frac{4r^{2} - L^{2}}{4r^{2} + L^{2}} \right)
$$

3. Convert the result from radians to degrees and take the absolute value.
The sign of the steering angle is handled elsewhere.

Returns: target steering angle in degrees.