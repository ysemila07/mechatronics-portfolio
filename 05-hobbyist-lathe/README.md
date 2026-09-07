# Hobbyist Lathe — Mechanical Design

**Course:** MECH311 (Mechanical Design)

Full mechanical design of a hobbyist metal lathe, from cutting-power sizing through to gearbox and
drivetrain layout, in Autodesk Inventor.

## Key specs

- Spindle speed range: **240–2000 RPM**, via a VFD driving a 750 W (1 HP) single-phase motor at
  1725 RPM (motor sourced from McMaster-Carr, ~$830.45).
- Drilling capacity 13 mm, spindle bore 18 mm, centre distance 500 mm, Morse taper MT2/MT3, three
  thread pitches supported (1, 1.25, 1.5 mm).
- Gearbox: 9 changeable + 2 fixed gears giving **15 possible speed ratio combinations**, 1.5 mm gear
  module, 8 bearings, dual V-belt drive (2 pulley ratios, belt lengths 711.2 mm and 1066.8 mm).
- Overall envelope 1250 × 500 × 627.5 mm; estimated weight ~70 kg (steel frame) + 5–10 kg motor.

## Design process

Started from a target material-removal rate (1 cm³/s), which gives a required cutting power of
~2.4 kW at the tool. Iterated the drivetrain design down to a working torque/power budget of
**1.67 kW / 7.97 Nm** at maximum spindle speed, then sized the gearbox and belt drive to deliver
that across the full 240–2000 RPM range.

## Visual assets

`Detailed Design/Lathe Demo Video.mov` in the original folder is a CAD walkthrough/animation of the
Inventor model — there's no physical build, so this is a design/CAD demo rather than footage of the
lathe running. CAD files (.ipt/.iam assemblies) aren't included in this repo (binary, not
git-friendly) — available on request or exportable as STEP files if needed for a portfolio site.
