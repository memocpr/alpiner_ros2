import csv
import math
import matplotlib.pyplot as plt
from pathlib import Path

base = Path('/home/evomrd/Desktop/AlpineR/alpiner_ros2/ros2_ws/src/ros2_application/evaluations')

ref_x, ref_y = [], []
with open(base / 'reference_path.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        ref_x.append(float(row['x']))
        ref_y.append(float(row['y']))

exe_x, exe_y = [], []
with open(base / 'executed_path.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        exe_x.append(float(row['x']))
        exe_y.append(float(row['y']))

# RMSE
errors = []
# use only last N points (e.g. last 100)
N = 100
exe_subset = list(zip(exe_x, exe_y))[-N:]

for x, y in exe_subset:
    min_dist = float('inf')
    for px, py in zip(ref_x, ref_y):
        dist = math.hypot(x - px, y - py)
        if dist < min_dist:
            min_dist = dist
    errors.append(min_dist)

rmse = math.sqrt(sum(e**2 for e in errors) / len(errors))
print(f'RMSE: {rmse:.3f} m')

# Mean heading error
exe_yaw = []
with open(base / 'executed_path.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        exe_yaw.append(float(row['yaw']))

ref_yaw = []
for i in range(len(ref_x) - 1):
    dx = ref_x[i + 1] - ref_x[i]
    dy = ref_y[i + 1] - ref_y[i]
    ref_yaw.append(math.atan2(dy, dx))
ref_yaw.append(ref_yaw[-1])

heading_errors = []
for x, y, yaw in zip(exe_x, exe_y, exe_yaw):
    min_idx = 0
    min_dist = float('inf')

    for i, (px, py) in enumerate(zip(ref_x, ref_y)):
        dist = math.hypot(x - px, y - py)
        if dist < min_dist:
            min_dist = dist
            min_idx = i

    dyaw = yaw - ref_yaw[min_idx]
    dyaw = math.atan2(math.sin(dyaw), math.cos(dyaw))
    heading_errors.append(abs(dyaw))

mean_heading_error = sum(heading_errors) / len(heading_errors)
print(f'Mean heading error: {mean_heading_error:.3f} rad')

# Plot
plt.plot(ref_x, ref_y, 'r', label='planned path')
plt.plot(exe_x, exe_y, 'g', label='executed path')
plt.axis('equal')
plt.legend()
plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.title('Path Following Evaluation')
plt.text(0.02, 0.98,
         f'RMSE: {rmse:.3f} m\nHeading: {mean_heading_error:.3f} rad',
         transform=plt.gca().transAxes,
         verticalalignment='top')
plt.show()