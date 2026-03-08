#!/bin/bash
# Complete setup: starts Gazebo + full Nav2 stack + RViz in separate terminals
# Usage: ./start_complete_stack.sh

WS_DIR="/home/evomrx22/Desktop/AlpineR/alpiner_ros2/ros2_ws"

echo "=== AlpineR Gazebo + Nav2 + RViz Complete Stack ==="
echo ""
echo "This will open 5 terminals for:"
echo "  Terminal 1: Gazebo simulation"
echo "  Terminal 2: Localization (UKF)"
echo "  Terminal 3: Mapping (RTAB-Map)"
echo "  Terminal 4: Nav2 navigation"
echo "  Terminal 5: RViz visualization"
echo ""
echo "Press ENTER to start, or Ctrl+C to cancel..."
read

# Terminal 1: Gazebo
echo "Starting Terminal 1: Gazebo..."
gnome-terminal --tab --title="Gazebo" -- bash -c "
cd $WS_DIR
source /opt/ros/humble/setup.bash
source install/setup.bash
echo 'Terminal 1: Launching Gazebo...'
ros2 launch robot_description gazebo.launch.py
exec bash
" 2>/dev/null || xterm -title "Gazebo" -hold -e "
cd $WS_DIR
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch robot_description gazebo.launch.py
" &

sleep 3

# Terminal 2: Localization
echo "Starting Terminal 2: Localization..."
gnome-terminal --tab --title="Localization" -- bash -c "
cd $WS_DIR
source /opt/ros/humble/setup.bash
source install/setup.bash
echo 'Terminal 2: Launching Localization (UKF)...'
ros2 launch ros2_application localization.launch.py use_sim_time:=true use_sim_odometry:=false use_sim_imu:=false
exec bash
" 2>/dev/null || xterm -title "Localization" -hold -e "
cd $WS_DIR
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch ros2_application localization.launch.py use_sim_time:=true use_sim_odometry:=false use_sim_imu:=false
" &

sleep 3

# Terminal 3: Mapping
echo "Starting Terminal 3: Mapping..."
gnome-terminal --tab --title="Mapping" -- bash -c "
cd $WS_DIR
source /opt/ros/humble/setup.bash
source install/setup.bash
echo 'Terminal 3: Launching Mapping (RTAB-Map)...'
ros2 launch ros2_application mapping.launch.py use_sim_time:=true use_sim_scan:=false
exec bash
" 2>/dev/null || xterm -title "Mapping" -hold -e "
cd $WS_DIR
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch ros2_application mapping.launch.py use_sim_time:=true use_sim_scan:=false
" &

sleep 3

# Terminal 4: Nav2
echo "Starting Terminal 4: Nav2..."
gnome-terminal --tab --title="Nav2" -- bash -c "
cd $WS_DIR
source /opt/ros/humble/setup.bash
source install/setup.bash
echo 'Terminal 4: Launching Nav2...'
ros2 launch nav2_bringup navigation_launch.py use_sim_time:=true params_file:=$WS_DIR/src/navigation2/nav2_bringup/params/nav2_params.yaml
exec bash
" 2>/dev/null || xterm -title "Nav2" -hold -e "
cd $WS_DIR
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch nav2_bringup navigation_launch.py use_sim_time:=true params_file:=$WS_DIR/src/navigation2/nav2_bringup/params/nav2_params.yaml
" &

sleep 3

# Terminal 5: RViz
echo "Starting Terminal 5: RViz..."
gnome-terminal --tab --title="RViz" -- bash -c "
cd $WS_DIR
source /opt/ros/humble/setup.bash
source install/setup.bash
echo 'Terminal 5: Launching RViz...'
ros2 run rviz2 rviz2 -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz
exec bash
" 2>/dev/null || xterm -title "RViz" -hold -e "
cd $WS_DIR
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run rviz2 rviz2 -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz
" &

echo ""
echo "All terminals launched!"
echo "Check each terminal for initialization messages."
echo "Once Nav2 is ready, use RViz to set goals."

