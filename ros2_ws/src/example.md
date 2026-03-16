````md
## Localization Debug Commands

### Build and Launch Localization
```bash
cd /home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_application robot_description
source install/setup.bash
ros2 launch ros2_application komatsu_localization.launch.py
```
Expected:
- Build finishes successfully.
- Nodes start:
  - `robot_state_publisher`
  - `ukf_node`
  - `sim_odometry_publisher`
  - `sim_imu_publisher`

Example log lines:
```
[INFO] robot_state_publisher: got segment base_link
[INFO] sim_odometry: Sim odometry integrates /cmd_vel into /odometry/raw
```

---

### Check Running Nodes
```bash
ros2 node list
ros2 node list | grep robot_state_publisher
```
Expected:
```
/robot_state_publisher
/sim_imu
/sim_odometry
/ukf_filter_node
```

---

### Check Available Topics
```bash
ros2 topic list
ros2 topic list | grep odom
ros2 topic list | grep imu
```

Expected important topics:
```
/odometry/raw
/odometry/filtered
/imu/data
/tf
/tf_static
/cmd_vel
```

---

### Verify Raw Odometry
```bash
ros2 topic hz /odometry/raw
ros2 topic echo /odometry/raw --once
```

Expected:
```
average rate: ~20 Hz
```

Example message:
```
header.frame_id: odom
child_frame_id: base_footprint
pose.pose.position.x: 0.0
```

---

### Verify IMU Data
```bash
ros2 topic hz /imu/data
ros2 topic echo /imu/data --once
```

Expected:
```
average rate: ~20 Hz
```

Example message:
```
header.frame_id: base_link
linear_acceleration.z: 9.81
orientation.w: 1.0
```

---

### Verify UKF Filtered Odometry
```bash
ros2 topic hz /odometry/filtered
ros2 topic echo /odometry/filtered --once
```

Expected:
```
average rate: ~30 Hz
```

Example message:
```
header.frame_id: odom
child_frame_id: base_footprint
```

---

### Verify TF: Odom → Base Footprint
```bash
ros2 run tf2_ros tf2_echo odom base_footprint
```

Expected:
Continuous transform output:
```
Translation: [x, y, 0]
Rotation: [0, 0, yaw]
```

Example:
```
Translation: [0.000, 0.000, 0.000]
Rotation: [0.000, 0.000, 0.000, 1.000]
```

---

### Verify TF: Base Footprint → Base Link
```bash
ros2 run tf2_ros tf2_echo base_footprint base_link
```

Expected:
Static transform from robot model:
```
Translation: [0, 0, 0]
Rotation: [0, 0, 0, 1]
```

Published by:
```
robot_state_publisher
```

---

### Inspect Static TF
```bash
ros2 topic echo /tf_static --once
```

Expected:
List of static transforms such as:
```
base_footprint -> base_link
base_link -> imu_link
base_link -> laser_frame
```

---

### Inspect TF Topics
```bash
ros2 topic list | grep tf
```

Expected:
```
/tf
/tf_static
```

---

### Find Source of Odometry Node
```bash
cd ~/Desktop/AlpineR/alpiner_ros2/ros2_ws/src
grep -R "sim_odometry_publisher" .
grep -R "broadcasts odom" .
```

Expected:
Location of implementation:
```
ros2_application/ros2_application/sim_odometry_publisher.py
```
````
