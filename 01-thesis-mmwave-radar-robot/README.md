# Autonomous Omni-Wheel Robot — mmWave Radar Navigation (Honours Thesis)

**Course:** ECTE498, Year 4 Sem 2 | **Supervisor:** Dr Prashan Premaratne
**Title:** *Designing an Autonomous Mobile Robot using Millimetre Wave Radar and Raspberry Pi* (Oct 2025)

## Overview

An omni-wheel mobile robot that uses a millimetre-wave (mmWave) radar sensor instead of camera/LiDAR
to detect obstacles and plan a path through an environment. The core motivation: mmWave radar is
unaffected by lighting conditions — it performed identically in full darkness as in daylight, which
is not true of vision-based sensing.

## Key results

- Obstacle-detection accuracy: average error **≈3.5 cm indoors, 6.3 cm outdoors, 6.7 cm in rain**,
  for objects between 0.3–1.2 m away. Metal surfaces gave near-perfect readings; cardboard was the
  weakest reflector — material affected accuracy more than distance or weather.
- Radar performance was **fully unaffected by lighting** (identical results in darkness).
- Mechanical: 20 mm ground clearance, radar mounted 11 cm off the ground at a 45° offset from wheel
  heading, open-loop motor control (no encoders) at 98% duty cycle, plastic omni-wheels.
- Software: global A* path planner, an occupancy-grid mapper built from radar scans, and a live web
  dashboard (`visual_dashboard_web.py`) for monitoring the robot in real time.

**Honest limitation:** the radar-to-map pipeline had stitching gaps between scans, so the robot did
not reliably complete a full maze/navigation test end-to-end. The planning algorithm (A*) worked
correctly on the generated maps — the weak link was map quality, not the planner.

## Code

- `code/mapper.py` — builds the occupancy map from radar scans
- `code/global_planner.py` — A* path planning over the map
- `code/movement.py` — motor/drive control
- `code/perception.py`, `radar_stream.py`, `readData_AWR1642.py` — radar data acquisition (TI AWR1642)
- `code/visual_dashboard_web.py` — live web dashboard for monitoring
- `code/run_robot_global.py` — top-level run script tying the above together
- `code/1642config.cfg` — radar sensor configuration
- `code/debug_visual.py` — debugging/visualisation helper

## Visual assets (not included in this repo — see note below)

The original project folder contains a demo video of the robot running (`run_robot.mp4`), a build
compilation video, and clean product photos of the finished robot. These are too large for a git
repo and weren't copied here — worth uploading to YouTube/Drive and linking from your CV/LinkedIn
if you want to show the robot in action.
