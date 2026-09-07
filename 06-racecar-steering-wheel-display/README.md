# Race Car Steering Wheel Display — UOW Motorsport (Team XPEDE)

**Course:** ECTE351 (Engineering Design and Management 3) | **Team:** XPEDE (5 members)

A custom STM32-based steering wheel display and driver control system built for UOW Motorsport's
electric formula-style vehicle. Four push buttons on the wheel let the driver adjust
torque-vectoring and traction-control settings from the cockpit; the selected values are sent over
the vehicle's CAN bus and shown on the display.

**Role on the team:** Finance & Procurement Lead. Contributed to the project's reports and
presentations, the ethics and management assessments, the innovation-fair poster, video demo
production, and stayed engaged with the hardware/software design to support the team where needed.

## Hardware

Custom PCB (`STM32_Steering_Display/`, KiCad project) fabricated via JLCPCB; components sourced from
JLCPCB, Mouser, RS, and the university's SECTE store.
- `STM32_Steering_Display.kicad_sch` / `.kicad_pcb` — main board schematic and layout
- `IO_switches.kicad_sch` — button/IO switch schematic

## Visual assets

`Steering Wheel Display & Driver Control System - XPEDE.mp4` — demo video of the working display
(transcript included alongside it in the original folder), and `XPEDE Trade Fair Vid.mp4` — trade
fair footage likely showing the board mounted in the car. Both too large for this repo; worth
uploading to YouTube/Drive and linking. `XPEDE A1 Poster.pdf` can be repurposed as a static graphic.
