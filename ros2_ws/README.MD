# Launching the robot model on RViz:
```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
source install/setup.bash
ros2 launch robot_description view_robot.launch.py
```

Or if you need a clean build:
```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws
rm -rf build/ install/ log/
colcon build --cmake-clean-cache
source install/setup.bash
ros2 launch robot_description view_robot.launch.py
```

# Gazebo + RViz + Nav2 (Complete Stack)

**Quick Start:** See **RVIZ_QUICKSTART.md** for step-by-step instructions to run Gazebo + RViz + Nav2 together and set navigation goals.

**Complete Guide:** See **GAZEBO_RVIZ_GUIDE.md** for detailed explanations of each component.

**Auto-Launcher (optional):** 
```bash
./start_complete_stack.sh
```

This opens 5 terminals automatically:
1. Gazebo simulation
2. Localization (UKF)
3. Mapping (RTAB-Map)
4. Nav2 navigation
5. RViz visualization

---

# See the TF
First launch the urdf on rviz:

Then in a new terminal, run the tf_view_frames node:
```bash
cd ~/alpiner_ros2/ros2_ws/src/robot_description/TFs
ros2 run tf2_tools view_frames
```


# Structure Overview

## Files & Directories

### URDF/Xacro Models
- **komatsu.urdf.xacro** - Main articulated wheel loader URDF model
  - Komatsu WA200 dimensions (8.35m length, 2.765m width)
  - Two-part chassis: rear (fixed) and front (articulated)
  - Articulation joint: ±22.4° steering with mimic joint for rear mimicking inverse front angle
  - Four wheels (cylinders) with continuous rotation
  
- **wheels.xacro** - Wheel macro for reusable wheel definitions
  - Defines parametric wheel macro (name, parent, x, y, radius, width)
  - Default: 0.80m radius, 0.65m width (23.5 R25 tire approximation)
  - All wheels rotate on Y-axis (ROS convention: x=forward, y=left, z=up)

### Launch Files
- **view_robot.launch.xml** - Visualization launcher
  - Runs `robot_state_publisher` to publish TF frames from URDF
  - Runs `joint_state_publisher_gui` for interactive joint control (steering angle)
  - Launches RViz2 with pre-configured view

### Configuration Files
- **urdf/urdf_config.rviz** - RViz2 visualization config (TFs, links, joints display)
- **package.xml** - ROS2 package metadata (ament_cmake build type)
- **CMakeLists.txt** - Installs urdf, launch, meshes, rviz directories

### TFs (Transform Frames)
- **frames_2026-02-25_10.22.47.gv/pdf** - Generated TF tree visualization
  - Shows kinematic chain: base_footprint → articulation_link → rear/front_chassis → wheels

### Meshes
- Empty directory (ready for 3D mesh files)




# ros2_interfaces

ROS2 package providing custom messages for the retrofit kit communication interface between the ROS2 navigation system and the machine control stack.

## Messages
* MachineSetAll — command message sent to the machine
* MachineSetOptions — command options and control flags
* MachineIndAll — full machine state feedback
* MachineIndOthers — additional machine state indicators
* MachineIndErrors — machine error states

## Setup

Create the package:
```bash
cd ~/ros2_ws/src
ros2 pkg create ros2_interfaces --build-type ament_cmake
```

Create the message directory and files:

## package.xml
Add required dependencies:

## CMakeLists.txt
Enable message generation:

## Build and Verify
```bash
cd ~/ros2_ws
colcon build --packages-select ros2_interfaces
source install/setup.bash

ros2 interface show ros2_interfaces/msg/MachineSetAll
ros2 interface show ros2_interfaces/msg/MachineIndAll
```
