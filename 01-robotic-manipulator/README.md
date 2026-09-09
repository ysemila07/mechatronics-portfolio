# Robotic Manipulator — Kinematic & Singularity Analysis (Group Project)

**Course:** MECH470 (Applied Topics in Mechatronics) | **Report title:** *Automatic Assembly of a Mobile Robot*
**Team:** 6 members

## Overview

A 5-DOF robotic arm designed and analysed in simulation for a pick-and-place task: picking up a
component (an M3 screw in the test case) and placing it. The arm geometry was custom-designed and
modelled in Autodesk Inventor; the kinematics, Jacobian, and singularity analysis were done in
MATLAB using the ARTE (A Robotics Toolbox for Education) library.

**Note:** this is a simulation-and-CAD project, not a physical build — there's no photo/video
evidence of a physical arm in the source material, and it should be described that way.

## Key results

- Denavit-Hartenberg parameters derived for the custom 5-DOF arm.
- Jacobian computed at two working configurations (pick-up and deposit poses for the M3 screw task);
  both configurations were **full rank (3/3)**, confirming the arm stayed singularity-free
  throughout the task.

## Full report

[`report/Final Report.pdf`](report/Final%20Report.pdf) — the group's full report, *Automatic Assembly of a Mobile Robot*.

## Code

- `code/kinematics.m`, `parameters.m` — forward kinematics and arm parameters
- `code/jacobian.m`, `jacobian_tool_config.m` — Jacobian computation
- `code/trajectory_plot.m`, `smooth_transition.m` — trajectory generation/plotting
- `code/robot_tooltip.m`, `run_robot.m` — tool-tip tracking and top-level run script

## Visual assets

None found in the original folder — this project is MATLAB scripts, Inventor CAD (.ipt/.iam), and
STL files only. If you want visuals for a portfolio, a screen-recording of the ARTE simulation or a
render of the Inventor model would be the way to generate one now.
