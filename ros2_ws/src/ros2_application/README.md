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

