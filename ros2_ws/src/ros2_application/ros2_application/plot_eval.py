import csv
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

plt.plot(ref_x, ref_y, 'r', label='planned path')
plt.plot(exe_x, exe_y, 'g', label='executed path')
plt.axis('equal')
plt.legend()
plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.title('Path Following Evaluation')
plt.show()