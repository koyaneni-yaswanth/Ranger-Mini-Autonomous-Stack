# Robot Assembly & Mechanical Enclosure Specifications

## 1. Enclosed Chassis Architecture
The robot features a three-tier enclosed structure protecting all internal computing and electronics:
- **Lower Drive Bay**: Houses 24V 30Ah LiFePO4 battery pack, 4x steering servo actuators, and 4x BLDC hub motors.
- **Middle Compute Bay**: Houses NVIDIA Jetson AGX Orin / Orin Nano developer carrier, isolated DC-DC converters (19V/12V/5V rails), dual 60mm PWM cooling fans, and dust filters.
- **Upper Deck**: CNC-machined 15mm 6061-T6 aluminum deck (`top_deck_link`) featuring a reinforced pedestal with a 4x M5 mounting pattern on 40mm PCD and central locating dowel for the Piper manipulator.

## 2. Elevated Sensor Mast
- 0.35m dual-column T-slot aluminum mast mounted at rear deck `(-0.18, 0.0, 0.015)`.
- **Livox Mid-360 LiDAR**: Summit mount (`z = +0.356m`), clearing the stowed arm for a 360° unobstructed horizontal sweep.
- **Intel RealSense D435i**: Mounted at `z = +0.24m` with a 15° forward-down pitch (`0.2618 rad`), covering tables from 0.40m to 0.85m height.
- **Hardware E-Stop**: High-visibility twist-to-release safety mushroom button with yellow bezel.
