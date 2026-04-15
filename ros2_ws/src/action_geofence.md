# Action Geofence: Georeferenced Field Map (Google Earth → QGIS → ROS2 Nav2)

## Overview

Create a GNSS-aligned occupancy map from aerial imagery for Nav2 global localization.

Pipeline:
Google Earth Pro → QGIS (GCP + Georeference) → ROS map (.pgm + .yaml) → Nav2 (GNSS)

---

## Step 1 — Extract Field Image (Google Earth Pro)

1. Open Google Earth Pro
2. Navigate to field
3. Draw polygon (field boundary)
4. Export image:
   File → Save → Save Image

Output:
simple_field.png

---

## Step 2 — Create Ground Control Points (GCP)

1. Add 4 placemarks (field corners)
2. Save each as:
   p_1.kmz
   p_2.kmz
   p_3.kmz
   p_4.kmz

---

## Step 3 — QGIS Processing

### 3.1 Load Data

- Load raster: simple_field.png
- Load vectors: p_1.kmz … p_4.kmz

---

### 3.2 Merge Points

Vector → Data Management → Merge Vector Layers

Output:
merged_points

---

### 3.3 Convert to UTM

Right click merged_points → Export → Save Features As

Set:
CRS: EPSG:32632

Output:
field_points_utm.gpkg

---

### 3.4 Georeference Image

Raster → Georeferencer

Steps:
1. Load simple_field.png
2. Add 4 GCP points:
    - Click image corner
    - Use "From Map Canvas"
    - Click corresponding UTM point

---

### 3.5 Run Georeferencing

Settings:
Transformation: Linear  
Target CRS: EPSG:32632  
Resampling: Nearest Neighbour  
Output: field_georef.tif

Run georeferencing

Result:
field_georef.tif aligned to UTM

---

## Step 4 — Convert to ROS Map

### 4.1 Export Raster

Right click field_georef → Export → Save As

Format: GeoTIFF  
Output: field_map.tif

---

### 4.2 Convert to PNG

gdal_translate -of PNG field_map.tif field_map.png

---

### 4.3 Convert to PGM

convert field_map.png field_map.pgm

---

### 4.4 Create YAML

Create file:
field_map.yaml

Content:

image: field_map.pgm  
resolution: 0.252289  
origin: [384944.09, 5202207.41, 0.0]  
negate: 0  
occupied_thresh: 0.65  
free_thresh: 0.196

---

## Step 5 — Integrate into Project

Copy files:

cp field_map.pgm <ros2_ws>/src/robot_bringup/maps/  
cp field_map.yaml <ros2_ws>/src/robot_bringup/maps/

---

## Step 6 — Build Workspace

cd <ros2_ws>  
rm -rf build install log  
source /opt/ros/humble/setup.bash  
colcon build --packages-select robot_bringup robot_description ros2_application  
source install/setup.bash

---

## Step 7 — Launch with GNSS

ros2 launch robot_bringup komatsu_gazebo_nav.launch.py \
use_mock_gnss:=true \
use_global_localization:=true \
use_static_map_to_odom:=false

---

## Step 8 — Verify

ros2 param get /map_server yaml_filename  
ros2 topic echo /gps/fix --once  
ros2 topic echo /odometry/gps --once  
ros2 topic echo /odometry/filtered --once  
ros2 run tf2_ros tf2_echo map odom

---

## Notes

- Map origin must align with GNSS datum (UTM)
- Wrong origin → robot drifting / "out of bounds"
- Nav2 map and Gazebo world are independent
- Georeferenced map is used only for planning/localization