# Fuzzy Logic & ANFIS Control

**Course:** ECTE441 — *Intelligent Control*

Two projects comparing classical and intelligent (fuzzy / neuro-fuzzy) control strategies, both in
MATLAB/Simulink simulation.

## Project 1 — PID vs Mamdani vs TSK/Sugeno on a DC motor
Built a Mamdani fuzzy controller (using MATLAB's classic "tipper" restaurant-service example as the
stepping-stone) and converted it to a TSK/Sugeno controller, then compared both against a
conventional PID controller on a DC motor speed task, with and without load.

**Result:** PID actually won on this task — rise time 0.038 s (no load) / 0.047 s (with load),
9.34% overshoot in both cases — though the fuzzy controllers likely had more tuning headroom than
was explored.

- `stage1-pid/` — PID baseline models (with/without load)
- `stage2-fis/` — Mamdani FIS files (tipper example → tipper_final)
- `stage3-fuzzy-motor/` — Mamdani fuzzy controller applied to the motor
- `stage4-tsk-motor/` — TSK/Sugeno controller applied to the motor

## Project 2 — Simulated mobile-robot obstacle avoidance: Fuzzy vs ANFIS
A simulated (not physical) mobile robot navigating around obstacles, comparing a hand-built Mamdani
fuzzy controller against a trained ANFIS controller. Both take ultrasonic distance + obstacle-location
inputs and output differential wheel speeds.

**Result:** both controllers reliably reached the target across 9+ runs from different start
positions/angles. ANFIS gave smoother, noise-filtered motion but took a longer route to the
target — a quantified trade-off between smoothness and directness.

- `project2-anfis-obstacle-avoidance/` — trained ANFIS models (`anfisvl400.fis`, `anfisvr400.fis`) and
  the fuzzy controller (`fuzzyrobot.fis`)

## Visual assets
Simulation plots exist in the original folder (trajectory plots, fuzzy control surfaces, ANFIS
training screenshot) but weren't copied here — worth pulling into a LinkedIn post to illustrate the
PID-vs-fuzzy-vs-ANFIS comparison.
