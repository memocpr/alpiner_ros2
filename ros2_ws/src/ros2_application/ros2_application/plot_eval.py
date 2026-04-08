import csv
import math
import matplotlib.pyplot as plt
from pathlib import Path

base = Path('~/Desktop/AlpineR/alpiner_ros2/ros2_ws/src/ros2_application/evaluations').expanduser()

ref_x, ref_y = [], []
with open(base / 'reference_path.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        ref_x.append(float(row['x']))
        ref_y.append(float(row['y']))

exe_x, exe_y = [], []
exe_time = []
with open(base / 'executed_path.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        exe_x.append(float(row['x']))
        exe_y.append(float(row['y']))
        exe_time.append(float(row['time']))

# RMSE
errors = []
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

cross_track_errors = errors
max_cross_track_error = max(abs(e) for e in cross_track_errors)
mean_cross_track_error = sum(abs(e) for e in cross_track_errors) / len(cross_track_errors)

print(f'Max cross-track error: {max_cross_track_error:.3f} m')
print(f'Mean cross-track error: {mean_cross_track_error:.3f} m')

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

# completion time
completion_time = exe_time[-1] - exe_time[0]
print(f'Completion time: {completion_time:.2f} s')

# summary CSV - overwrite with latest result only
summary_path = base / 'metrics_summary.csv'

with open(summary_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'run',
        'rmse_m',
        'mean_heading_error_rad',
        'max_cross_track_error_m',
        'mean_cross_track_error_m',
        'completion_time_s'
    ])
    writer.writerow([
        'latest',
        rmse,
        mean_heading_error,
        max_cross_track_error,
        mean_cross_track_error,
        completion_time
    ])

# Plot
plt.plot(ref_x, ref_y, 'r', label='planned path')
plt.plot(exe_x, exe_y, 'g', label='executed path')
plt.axis('equal')
plt.legend()
plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.title('Path Following Evaluation')
plt.text(0.02, 0.98,
         f'RMSE: {rmse:.3f} m\n'
         f'Max CTE: {max_cross_track_error:.3f} m\n'
         f'Mean CTE: {mean_cross_track_error:.3f} m\n'
         f'Heading: {mean_heading_error:.3f} rad\n'
         f'Time: {completion_time:.2f} s',
         transform=plt.gca().transAxes,
         verticalalignment='top')

# Cross-track error vs time
cte_time = exe_time[-N:]
cte_values = cross_track_errors

plt.figure()
plt.plot(cte_time, cte_values)
plt.xlabel('time [s]')
plt.ylabel('cross-track error [m]')
plt.title('Cross-Track Error vs Time')
plt.grid()

# Heading error vs time
plt.figure()
plt.plot(exe_time, heading_errors)
plt.xlabel('time [s]')
plt.ylabel('heading error [rad]')
plt.title('Heading Error vs Time')
plt.grid()

# Summary table plot
rows = []
with open(summary_path, newline='') as f:
    reader = csv.reader(f)
    headers = next(reader)
    for r in reader:
        rows.append(r)

plt.figure()
plt.axis('off')
table = plt.table(
    cellText=rows,
    colLabels=headers,
    loc='center'
)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.5)
plt.title('Evaluation Summary')

plt.show()