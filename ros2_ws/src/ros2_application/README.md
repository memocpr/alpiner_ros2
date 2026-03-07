# ros2_application

## Action 3: Localization pipeline (UKF)

This package now includes a minimal local-test localization setup:

- `launch/localization.launch.py`
- `config/ukf_params.yaml`
- `ros2_application/sim_odometry_publisher.py`
- `ros2_application/sim_imu_publisher.py`

### Topics

- Inputs:
  - `/odometry/raw` (`nav_msgs/msg/Odometry`)
  - `/imu/data` (`sensor_msgs/msg/Imu`)
- Output:
  - `/odometry/filtered` (`nav_msgs/msg/Odometry`)
- TF:
  - `odom -> base_link` (published by `ukf_node`)

### Run

```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_application
source install/setup.bash
ros2 launch ros2_application localization.launch.py
```

### Notes

- `robot_localization` must be installed in the environment.
- You can disable simulation sources with:
  - `use_sim_odometry:=false`
  - `use_sim_imu:=false`

## Action 4: Mapping pipeline (RTAB-Map)

This package now includes a minimal local-test mapping setup:

- `launch/mapping.launch.py`
- `config/rtabmap_params.yaml`
- `ros2_application/sim_scan_publisher.py`

### Topics

- Inputs:
  - `/odometry/filtered` (`nav_msgs/msg/Odometry`)
  - `/scan` (`sensor_msgs/msg/LaserScan`)
- Output:
  - `/map`
- TF:
  - `map -> odom` (published by RTAB-Map)
  - `base_link -> laser_frame` (static TF, only in sim scan mode)

### Run

```bash
cd /home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws
colcon build --packages-select ros2_application
source install/setup.bash
ros2 launch ros2_application mapping.launch.py
```

### Hardware Adaptation

Switch from simulated to real sensor input:

```bash
# Option A: Disable sim scan, remap to real topic
ros2 launch ros2_application mapping.launch.py use_sim_scan:=false scan_topic:=/your_real_scan_topic

# Option B: Use dedicated hardware launch (cleaner)
ros2 launch ros2_application mapping_hw.launch.py scan_topic:=/your_real_scan_topic laser_frame:=/your_laser_frame
```

### Notes

- Start Action 3 first so `/odometry/filtered` is available.
- For retrofit kit: update `scan_topic` and `laser_frame` to match actual hardware TF tree.
- Static TF `base_link -> laser_frame` will be provided by your hardware driver or robot_description URDF.
