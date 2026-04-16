# Action Geofence: Georeferenced Field Map + Gazebo Aerial World

## Overview

Create:
- a **georeferenced UTM map** for Nav2 / GNSS localization
- a **local Gazebo aerial world** for simulation and visual alignment

Important:
- **Nav2 map** and **Gazebo world** are different assets
- **UTM coordinates** are correct for the ROS map
- **local coordinates** are required for Gazebo Classic spawning / simulation

Pipeline:
Google Earth Pro → QGIS (GCP + Georeference) → occupancy map (`.pgm` + `.yaml`) → Nav2  
and in parallel:  
Google Earth Pro image → Gazebo textured ground plane

---

## Step 1 — Extract Field Image (Google Earth Pro)

1. Open Google Earth Pro
2. Navigate to the field
3. Mark the field corners
4. Export the image:
   - `File → Save → Save Image`

Output:
- `simple_field.png`

---

## Step 2 — Create Ground Control Points (GCP)

1. Add 4 placemarks on the field corners
2. Save them as:
   - `p_1.kmz`
   - `p_2.kmz`
   - `p_3.kmz`
   - `p_4.kmz`

---

## Step 3 — QGIS Georeferencing

### 3.1 Load Data

Load:
- raster: `simple_field.png`
- vectors: `p_1.kmz ... p_4.kmz`

### 3.2 Merge Points

Menu:
- `Vector → Data Management → Merge Vector Layers`

Output:
- merged point layer

### 3.3 Convert to UTM

Right click merged points:
- `Export → Save Features As`

Set:
- CRS: `EPSG:32632`

Output:
- `field_points_utm.gpkg`

### 3.4 Georeference Image

Menu:
- `Raster → Georeferencer`

Steps:
1. Load `simple_field.png`
2. Add 4 GCP points:
   - click image corner
   - use **From Map Canvas**
   - select corresponding UTM point

### 3.5 Run Georeferencing

Settings:
- Transformation: `Linear`
- Target CRS: `EPSG:32632`
- Resampling: `Nearest Neighbour`
- Output: `field_georef.tif`

Result:
- `field_georef.tif`

---

## Step 4 — Create Occupancy Map for Nav2

Important:
- Do **not** convert the aerial image directly to `.pgm`
- That only changes file format and makes RViz treat the whole aerial image as a map
- You must create a **binary occupancy mask**

### 4.1 Create Field Polygon in QGIS

1. Create new GeoPackage layer:
   - geometry: `Polygon`
   - CRS: `EPSG:32632`
   - file: `field_polygon.gpkg`
   - layer: `field_polygon`

2. Enable editing
3. Draw polygon using the 4 field corners
4. Right click to finish
5. Click **OK**
6. Click **Save Edits**
7. Disable editing

Verify:
```bash
ogrinfo field_polygon.gpkg field_polygon -al -so