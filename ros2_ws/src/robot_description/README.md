# Robot Description Package

## Overview

This package contains the URDF model, visualization configuration, and Gazebo simulation setup for the Komatsu articulated loader.

## Contents

- **URDF Models**:
  - `urdf/komatsu.urdf.xacro`: Base robot model with articulated steering
  - `urdf/komatsu_gazebo.urdf.xacro`: Gazebo-enhanced model with sensors and physics
  - `urdf/wheels.xacro`: Wheel macro with collision and inertia properties
  
- **Launch Files**:
  - `launch/view_robot.launch.py`: Visualize robot in RViz with joint state publisher
  - `launch/gazebo.launch.py`: Launch Gazebo simulation with robot

- **Worlds**:
  - `worlds/farm_field.world`: Simple farm field environment for testing

- **RViz Configs**:
  - `rviz/urdf_config.rviz`: RViz configuration for robot visualization

## Robot Specifications

Based on Komatsu WA380 articulated wheel loader:
- **Overall length**: 8.35 m
- **Wheelbase**: 3.03 m
- **Width**: 2.765 m (over tires)
- **Track width**: 2.16 m
- **Ground clearance**: 0.455 m
- **Overall height**: 3.395 m
- **Articulation angle**: ±0.35 rad (±20°)
- **Wheel radius**: ~0.80 m

## TF Tree

```
map
└── odom
    └── base_footprint
        └── base_link
            ├── articulation_link
            │   ├── rear_chassis
            │   │   ├── rear_left_wheel
            │   │   └── rear_right_wheel
            │   └── front_chassis
            │       ├── front_left_wheel
            │       └── front_right_wheel
            ├── laser_frame
            └── imu_link
```

## Usage

### Visualize in RViz

```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
source install/setup.bash
ros2 launch robot_description view_robot.launch.py
```

### Gazebo Simulation (Action 7)

**Prerequisites**: Install Gazebo and gazebo_ros packages:

```bash
sudo apt update
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros
```

**Launch Gazebo simulation**:

```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
source install/setup.bash
ros2 launch robot_description gazebo.launch.py
```

**Gazebo features**:
- Differential drive plugin for cmd_vel consumption
- Simulated LiDAR sensor (360° scan, 50m range)
- IMU sensor
- Ground truth odometry
- Realistic physics with wheel friction and inertia

**Topics provided by Gazebo**:
- `/odom` (nav_msgs/Odometry) - Wheel odometry
- `/scan` (sensor_msgs/LaserScan) - LiDAR data
- `/imu/data` (sensor_msgs/Imu) - IMU data
- `/ground_truth/odom` (nav_msgs/Odometry) - Perfect ground truth

**Control interface**:
- `/cmd_vel` (geometry_msgs/Twist) - Velocity commands

## Integration with Navigation Stack

See `ros2_application/README.md` for complete integration instructions (Action 7).

Quick start with full stack:

```bash
# Terminal 1: Launch Gazebo
ros2 launch robot_description gazebo.launch.py

# Terminal 2: Launch full navigation stack
ros2 launch ros2_application rviz_integration.launch.py \
  use_sim_odometry:=false \
  use_sim_imu:=false \
  use_sim_scan:=false \
  use_cmd_vel_joint_sim:=false
```

## Notes

- Gazebo URDF includes collision and inertial properties required for physics simulation
- Base URDF (komatsu.urdf.xacro) is suitable for RViz visualization and real hardware
- Articulated steering is simplified to differential drive in Gazebo for initial testing
- For full articulated steering simulation, future work will add ros2_control integration

## Troubleshooting

### Robot not appearing in Gazebo

**Issue**: Robot model doesn't show in Gazebo after launch.

**Fixes applied**:
1. **Xacro include paths**: Changed relative paths to absolute using `$(find robot_description)` syntax
   - `komatsu_gazebo.urdf.xacro`: Fixed include path for `komatsu.urdf.xacro`
   - `komatsu.urdf.xacro`: Fixed include path for `wheels.xacro`

2. **Spawn timing**: Added 3-second delay to `spawn_entity` to ensure Gazebo and `robot_state_publisher` are ready

**Test script**: Use `scripts/test_gazebo.sh` to verify setup

### Gazebo "Address already in use" error

Clean up existing Gazebo processes:
```bash
killall -9 gzserver gzclient
```

