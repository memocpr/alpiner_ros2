# Action 7 Quick Reference

## Launch Gazebo Only
```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
source install/setup.bash
ros2 launch robot_description gazebo.launch.py
```

## Full Navigation Stack with Gazebo

### Terminal 1: Gazebo Simulation
```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
source install/setup.bash
ros2 launch robot_description gazebo.launch.py
```

### Terminal 2: Localization
```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
source install/setup.bash
ros2 launch ros2_application localization.launch.py \
  use_sim_odometry:=false \
  use_sim_imu:=false
```

### Terminal 3: Mapping
```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
source install/setup.bash
ros2 launch ros2_application mapping.launch.py \
  use_sim_scan:=false
```

### Terminal 4: Navigation + RViz
```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
source install/setup.bash
ros2 launch ros2_application rviz_integration.launch.py \
  use_sim_scan:=false \
  use_cmd_vel_joint_sim:=false
```

## Monitor Topics

### View Odometry
```bash
ros2 topic echo /odom
```

### View LiDAR Scan
```bash
ros2 topic echo /scan
```

### View IMU
```bash
ros2 topic echo /imu/data
```

### View Ground Truth (for evaluation)
```bash
ros2 topic echo /ground_truth/odom
```

### View Velocity Commands
```bash
ros2 topic echo /cmd_vel
```

## Check TF Tree
```bash
ros2 run tf2_tools view_frames
evince frames.pdf
```

## Gazebo GUI Controls
- **Pan**: Middle mouse button + drag
- **Rotate**: Left mouse button + drag
- **Zoom**: Scroll wheel
- **Select**: Left click on model
- **Move model**: Select + translate/rotate tools

## Troubleshooting

### Gazebo not installed
```bash
sudo apt update
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros
```

### URDF errors
```bash
# Validate URDF
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
source install/setup.bash
check_urdf install/robot_description/share/robot_description/urdf/komatsu_gazebo.urdf.xacro
```

### Robot not spawning
- Check Gazebo terminal for error messages
- Verify `/robot_description` topic: `ros2 topic echo /robot_description`
- Check if spawn_entity.py completed successfully

### No sensor data
- Verify Gazebo simulation is running (not paused)
- Check topic list: `ros2 topic list`
- Check topic frequency: `ros2 topic hz /scan`

## Files Location

| Item | Path |
|------|------|
| Gazebo URDF | `src/robot_description/urdf/komatsu_gazebo.urdf.xacro` |
| Gazebo Launch | `src/robot_description/launch/gazebo.launch.py` |
| World File | `src/robot_description/worlds/farm_field.world` |
| Package README | `src/robot_description/README.md` |
| Action Summary | `ACTION7_SUMMARY.md` |
| Test Script | `test_action7.sh` |

## Key Parameters

### Differential Drive
- Wheel separation: 2.16 m
- Wheel diameter: 1.6 m
- Max torque: 5000 N⋅m

### LiDAR
- Range: 0.3 - 50 m
- FOV: 360°
- Update rate: 10 Hz
- Samples: 360

### IMU
- Update rate: 100 Hz
- Frame: imu_link

## Documentation
- Full details: `ACTION7_SUMMARY.md`
- Integration guide: `src/ros2_application/README.md` (Action 7 section)
- Package info: `src/robot_description/README.md`

