# ROS2 Based Robotic Automation
ROS2-based software implementation for the AlpineR project, which focuses on developing an adaptable and testable automation retrofit kit for a construction loader. The project includes path planning and tracking for farm field tasks with repetitive moves.

Thesis documents are on the [wiki](https://gitlab.ti.bfh.ch/groups/mse_cs/spring26/master_thesis/-/wikis/home) page

# Planning and Timeline

* [Project Roadmap](https://gitlab.ti.bfh.ch/groups/mse_cs/spring26/-/roadmap?state=all&sort=START_DATE_ASC&layout=WEEKS&timeframe_range_type=CURRENT_QUARTER&progress=WEIGHT&show_progress=true&show_milestones=true&milestones_type=ALL&show_labels=false)
* [Epic board](https://gitlab.ti.bfh.ch/groups/mse_cs/spring26/-/epic_boards)
* [Issue board](https://gitlab.ti.bfh.ch/groups/mse_cs/spring26/-/boards)

# Milestones

## FEB – Foundations & Planning
**Milestone: Foundations & Planning Complete** (Due: Feb 28, 2026)
- Project setup
- Requirements + evaluation metrics
- System architecture
- Literature preparation
- URDF model creation

## MAR – Fundamentals + Initial Implementation
**Milestone: ROS2 & Nav2 Integration Complete** (Due: Mar 31, 2026)
- ROS2 communication between layers
- ROS2 controller + HW interface
- Nav2 integration + Basic path following
- E2E test on mock component
- Real HW test

## APR – Customization
**Milestone: Custom Navigation & Kinematic Model Complete** (Due: Apr 30, 2026)
- Improvement + Bugfix
- Vehicle kinematic model creation
- Custom navigation implementation
- Real HW test 2

## MAY – Algorithm Creation
**Milestone: Field Geometry & AOG Integration Complete** (Due: May 31, 2026)
- Improvement + Bugfix 2
- Field Geometry + Row Generation
- AOG adaptation
- Real HW test 3

## JUN – Complex Cases
**Milestone: Complex Cases & Integration Complete** (Due: Jun 30, 2026)
- Improvement + Bugfix 3
- Complex cases
- Real HW test 4
- Improvement + Bugfix 4

## JUL – Finalization
**Milestone: Thesis Complete & Submitted** (Due: Jul 30, 2026)
- Full Thesis Draft Assembly
- Supervisor Review + Revisions
- Final Formatting + Submission


# Getting Started
clone the repository and navigate to the ROS2 workspace:
```bash
git clone git@gitlab.ti.bfh.ch:mse_cs/spring26/master_thesis/alpiner/alpiner_ros2.git
cd alpiner_ros2/ros2_ws
```
Build, source the workspace:
```bash
colcon build --symlink-install
source install/setup.bash
```