# Mechanical Assembly & Enclosure Specifications

## 1. Structural Enclosure Architecture
The robot features a purpose-built three-tier enclosed body eliminating exposed cabling and providing IP54 protection for internal electronics:

1. **Lower Bay (Drive & Battery)**:
   - Houses the 24V 30Ah Lithium-Iron-Phosphate (LiFePO4) main traction battery.
   - Accommodates 4x steering servos and 4x hub motor BLDC drive controllers.
   - Dual CAN transceiver wiring looms running through reinforced bulkhead grommets.

2. **Middle Bay (Compute & Power Electronics)**:
   - Houses the NVIDIA Jetson AGX Orin / Orin Nano developer carrier.
   - Features active forced-air cross-flow cooling with dual 60mm PWM fans and intake dust filters.
   - Houses DC-DC isolated buck-boost converters:
     * 24V -> 19V @ 5A (Jetson compute rail)
     * 24V -> 12V @ 8A (Sensors & networking switch)
     * 24V -> 5V @ 4A (Auxiliary logic & USB hub)

3. **Upper Deck (Structural Top Deck)**:
   - Precision CNC-machined 15mm 6061-T6 aluminum deck (`top_deck_link`).
   - Reinforced mounting pedestal at `(0.15, 0.0, 0.015)` with 4x M5 bolt pattern on 40mm PCD with locating dowel.
   - Quick-disconnect locking collar with IP67 Amphenol hybrid power/CAN connector.

## 2. Elevated Sensor Mast
- **Mast Uprights**: Dual 20x20mm T-slot aluminum extrusions mounted at rear center `(-0.18, 0.0, 0.015)`.
- **LiDAR Placement**: Elevated Livox Mid-360 at mast summit (`z = +0.356m` relative to deck). This elevated position ensures 360° laser sweep clears the top of the folded/transporting Piper arm.
- **Camera Placement**: Intel RealSense D435i mounted at `z = +0.24m` on an adjustable tilt plate fixed at 15° pitch down. This angle ensures full coverage of tables from 0.40m to 0.85m height at 0.4m to 2.0m distance.
- **E-Stop Assembly**: Red mushroom twist-to-release safety switch with high-visibility yellow guard ring mounted at the top-rear of the mast.
