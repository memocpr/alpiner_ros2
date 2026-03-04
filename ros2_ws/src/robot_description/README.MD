
# Launching the urdf on rviz:
```bash
cd /home/evomrx22/Desktop/AlpineR/ros2_ws
colcon build 
source install/setup.bash
source /opt/ros/humble/setup.bash
ros2 launch robot_description view_robot.launch.xml
```

# See the TF
First launch the urdf on rviz:

Then in a new terminal, run the tf_view_frames node:
```bash
cd /home/evomrx22/Desktop/AlpineR/ros2_ws/src/robot_description/TFs
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

# Documentation