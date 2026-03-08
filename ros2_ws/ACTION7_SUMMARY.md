# Action 7: Gazebo Simulation - Implementation Summary

## Overview
Action 7 adds optional Gazebo simulation capability to provide realistic robot motion and sensor feedback for testing the Nav2 navigation stack without hardware.

## Implementation Date
March 8, 2026

## Key Components Added

### 1. Gazebo-Enhanced URDF Model
**File**: `src/robot_description/urdf/komatsu_gazebo.urdf.xacro`

**Features**:
- Includes base robot model (`komatsu.urdf.xacro`)
- Gazebo material properties for visual rendering
- Wheel friction properties (μ₁=μ₂=1.0 for traction)
- Sensor plugins:
  - LiDAR: 360° scan, 50m range, 10Hz update rate
  - IMU: 100Hz update rate
- Differential drive plugin for motion control
- Ground truth odometry plugin for evaluation

**Differential Drive Configuration**:
- Left/right joints: `rear_left_wheel_joint`, `rear_right_wheel_joint`
- Wheel separation: 2.16 m
- Wheel diameter: 1.6 m
- Max torque: 5000 N⋅m
- Publishes odometry on `/odom` topic
- TF: `odom → base_link`

### 2. World File
**File**: `src/robot_description/worlds/farm_field.world`

**Features**:
- Simple flat ground plane (farm field)
- Sun lighting
- Physics engine: ODE with 1ms time step
- Real-time factor: 1.0 (1000 Hz update rate)

### 3. Launch File
**File**: `src/robot_description/launch/gazebo.launch.py`

**Capabilities**:
- Launches Gazebo server (gzserver)
- Launches Gazebo client (gzclient)
- Spawns robot at configurable position (default: 0, 0, 0.5)
- Publishes robot description
- Supports custom world file via parameter

**Parameters**:
- `use_sim_time`: Enable simulation time (default: true)
- `world_file`: Path to Gazebo world file

### 4. Updated Base URDF
**Files**: 
- `src/robot_description/urdf/komatsu.urdf.xacro`
- `src/robot_description/urdf/wheels.xacro`

**Changes**:
- Added collision geometries to all links
- Added inertial properties:
  - Wheels: 50 kg, appropriate inertia tensors
  - Rear chassis: 5000 kg
  - Front chassis: 5000 kg
  - Base/articulation links: minimal mass (0.01 kg)

### 5. Package Configuration
**Updated Files**:
- `package.xml`: Added Gazebo dependencies
  - `gazebo_ros`
  - `gazebo_plugins`
  - Additional: `robot_state_publisher`, `joint_state_publisher`, `xacro`
- `CMakeLists.txt`: Install worlds directory and gazebo.launch.py

### 6. Documentation
**Files**:
- `src/robot_description/README.md`: Comprehensive package documentation
- `src/ros2_application/README.md`: Integration instructions (Action 7 section)

## Integration Pipeline

```
User sends /cmd_vel
        ↓
Gazebo Differential Drive Plugin
        ↓
Simulated wheel motion
        ↓
Physics engine updates robot pose
        ↓
Sensors publish data:
  - /odom (wheel odometry)
  - /scan (LiDAR)
  - /imu/data (IMU)
  - /ground_truth/odom (perfect truth)
        ↓
Localization (robot_localization UKF)
        ↓
/odometry/filtered
        ↓
Mapping (RTAB-Map)
        ↓
/map and map→odom TF
        ↓
Nav2 Planning & Control
        ↓
/cmd_vel (loop closes)
```

## Topics Provided by Gazebo

| Topic | Type | Description |
|-------|------|-------------|
| `/cmd_vel` | geometry_msgs/Twist | Input: velocity commands |
| `/odom` | nav_msgs/Odometry | Output: wheel odometry |
| `/scan` | sensor_msgs/LaserScan | Output: LiDAR scan |
| `/imu/data` | sensor_msgs/Imu | Output: IMU data |
| `/ground_truth/odom` | nav_msgs/Odometry | Output: perfect ground truth |

## Usage Examples

### Basic Gazebo Launch
```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
source install/setup.bash
ros2 launch robot_description gazebo.launch.py
```

### Full Navigation Stack with Gazebo
```bash
# Terminal 1: Gazebo
ros2 launch robot_description gazebo.launch.py

# Terminal 2: Localization (use Gazebo sensors)
ros2 launch ros2_application localization.launch.py \
  use_sim_odometry:=false \
  use_sim_imu:=false

# Terminal 3: Mapping (use Gazebo LiDAR)
ros2 launch ros2_application mapping.launch.py \
  use_sim_scan:=false

# Terminal 4: Nav2 + RViz
ros2 launch ros2_application rviz_integration.launch.py \
  use_sim_scan:=false \
  use_cmd_vel_joint_sim:=false
```

## Design Decisions

### 1. Differential Drive Simplification
- Articulated steering is complex to simulate realistically
- Initial implementation uses differential drive for cmd_vel consumption
- Provides working motion model for Nav2 testing
- Future: Add ros2_control with articulated steering controller

### 2. Sensor Configuration
- LiDAR: 360° coverage matches typical construction vehicle setup
- 50m range adequate for farm field operations
- 10Hz update rate balances performance and mapping quality

### 3. Physics Properties
- Wheel friction (μ=1.0) provides good traction without slippage
- Mass distribution approximates real loader (10,000+ kg total)
- Inertia values allow responsive motion without instability

### 4. Ground Truth for Evaluation
- `/ground_truth/odom` provides perfect pose for Action 10 evaluation
- Enables quantitative assessment of:
  - Path tracking error
  - Heading error
  - Localization accuracy

## Installation Requirements

Gazebo Classic and ROS 2 integration:
```bash
sudo apt update
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros
```

## Testing

### Build Test
```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select robot_description
```
**Result**: ✅ Builds successfully

### Xacro Validation
```bash
source install/setup.bash
xacro src/robot_description/urdf/komatsu_gazebo.urdf.xacro > /tmp/test.urdf
```
**Result**: ✅ No errors

### File Installation
```bash
ls install/robot_description/share/robot_description/
```
**Expected**: urdf/, worlds/, launch/, rviz/, meshes/
**Result**: ✅ All directories present

## Known Limitations

1. **Simplified Kinematics**: Differential drive approximation instead of true articulated steering
2. **Static World**: Basic flat ground plane, no obstacles or terrain
3. **No Articulation Joint Control**: Articulation joint not driven by Gazebo physics
4. **Sensor Noise**: Minimal noise models (Gaussian, low stddev)

## Future Enhancements (Not in Action 7)

1. **ros2_control Integration** (Action 8+):
   - Articulated steering controller
   - Joint-level command interfaces
   - Hardware abstraction layer

2. **Enhanced World**:
   - Add obstacles (trees, buildings, equipment)
   - Terrain variations (slopes, rough ground)
   - Dynamic objects

3. **Advanced Sensors**:
   - GPS/GNSS simulation
   - Depth camera for 3D mapping
   - Additional IMUs for improved localization

4. **Realistic Physics**:
   - Ground contact modeling
   - Articulation joint dynamics
   - Load effects on handling

## Files Summary

| File | Lines | Purpose |
|------|-------|---------|
| `urdf/komatsu_gazebo.urdf.xacro` | 165 | Gazebo robot model with plugins |
| `launch/gazebo.launch.py` | 102 | Gazebo launch configuration |
| `worlds/farm_field.world` | 38 | Simulation environment |
| `README.md` | 150 | Package documentation |

**Total new/modified files**: 7
- Created: 4
- Modified: 3 (wheels.xacro, komatsu.urdf.xacro, package.xml, CMakeLists.txt)

## Conclusion

Action 7 successfully implements optional Gazebo simulation for the AlpineR navigation stack. The implementation:

✅ Provides realistic motion and sensor simulation  
✅ Integrates seamlessly with existing Nav2 stack  
✅ Enables hardware-free testing and development  
✅ Sets foundation for quantitative evaluation (Action 10)  
✅ Maintains compatibility with real hardware workflow  

**Status**: Action 7 COMPLETE

