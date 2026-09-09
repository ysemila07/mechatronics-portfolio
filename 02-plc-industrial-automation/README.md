# Industrial Automation & PLC Control (5 deliverables)

**Course:** MECH470 (Applied Topics in Mechatronics)

Five separate PLC/simulation deliverables built in Siemens TIA Portal (ladder logic) and
MATLAB/Simulink/Simscape. All are simulated plant models rather than physical hardware builds.

## Water Heating & Pumping Station
Ladder logic for a heated process tank. Heater cuts off above 40°C; the process tank is held at
30°C ±2°C. The built-in TIA Portal "scale" block didn't give usable results from the raw sensor
signal, so a custom calibration equation was derived instead: `Temp = -RawValue/556 + 63.6`. The
heater is latched on for a minimum 5 seconds via a TON timer to protect its service life.
See `water-heating-pumping/screenshots/ladder-logic-overview.png` and the full lab report at [`water-heating-pumping/report/Lab Report.pdf`](water-heating-pumping/report/Lab%20Report.pdf).

## Warehouse Lift
Ladder logic for a 3-floor lift using a laser distance sensor (4–20 mA over a 500 Ω resistor,
scaled into a 0–32767 PLC analogue input). Motor control is 3-point: ~16,000 = stop, ~32,000 = up,
0 = down, with a 20 mm hysteresis/neutral band to prevent relay chatter near floor stops. Floor
positions were empirically calibrated (e.g. floor 2 ≈ 400–420 mm). See `warehouse-lift/screenshots/`
(system diagram + 4 ladder-logic screens). Full report: [`warehouse-lift/report/Lab Report.pdf`](warehouse-lift/report/Lab%20Report.pdf).

## Robotic Sorting Cell
Ladder logic for a block-sorting cell using a shade/colour sensor. Thresholds were empirically
determined: painted block 3500–7000, unpainted 1000–3500 (analogue range). `IN_RANGE` blocks are
gated by a 3-second `TON` debounce to stop false double-triggers. Fault detection covers "robot
malfunction" and "no blocks on the slide"; a third alert (sensor/light failure) was scoped but not
finished in the time available. See `robot-sorter/screenshots/ladder-logic-overview.png` and the full report at [`robot-sorter/report/Lab Report.pdf`](robot-sorter/report/Lab%20Report.pdf).

## Motor Modelling (individual — Simulink/Simscape)
Models a DC servo motor actuating the oxygen valve on a miniature rocket engine. Motor specs:
MT-2240-AMYAN servo, 4 Ω armature resistance, 7.7 mH inductance, 0.115 Nm/A torque constant.
Files: `motor-modelling/lab6_base_workspace*.slx` (base model, post motor-parameter fit, valve
assembly, variable load). Full report: [`motor-modelling/report/Lab Report.pdf`](motor-modelling/report/Lab%20Report.pdf).

## Feedback Control (individual — Simulink)
PID tuning for the same motor/valve system. Ziegler-Nichols tuning gave Kp = 166, Ki = 665,
Kd = 10.4 (from ultimate gain Ku = 277, ultimate period Tu = 0.5 s), compared against a manually
fine-tuned PID and the rocket-engine command sequence. Files: `feedback-control/lab7_base_workspace*.slx`. Full report: [`feedback-control/report/Lab Report.pdf`](feedback-control/report/Lab%20Report.pdf).

## Visual assets
The screenshots under each subfolder are simulation/ladder-logic views, not photos of physical
hardware — none of these five deliverables involved a physical build.
