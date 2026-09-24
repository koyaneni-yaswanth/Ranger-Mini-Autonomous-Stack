# Manipulator Add / Remove Field Operator Guide

This field operations guide provides clear step-by-step instructions for mechanically and electrically attaching or removing the 6-DOF robotic manipulator from the Ranger Mini AMR platform, along with the single-parameter software reconfiguration.

---

## Phase 1: Adding the Manipulator (AMR -> Mobile Manipulator)

### Step 1: Mechanical Mounting
1. Power down the Ranger Mini AMR using the main key switch. Ensure the Emergency Stop push button is depressed.
2. Position the Piper arm base plate onto `manipulator_mount` on the top deck plate. Align the 4 bolt holes with the deck mounting pattern.
3. Insert 4x M5x16 mm high-tensile socket-head cap screws with split-lock washers.
4. Torque each bolt crosswise to **4.8 N·m** using a calibrated torque hex key.
5. Inspect clearance: Ensure the arm base does not obstruct the 360-degree LiDAR optical aperture or RealSense camera field of view.

### Step 2: Electrical & Bus Connection
1. Connect the 24V power supply cable to the XT30/XT60 power bulkhead connector on the top deck. Press firmly until seated.
2. Mate the 9-pin D-sub or Hirose CAN bus connector into the designated CAN port. Tighten the jack thumbscrews.
3. Route and secure cables through the strain-relief chassis clips to prevent pinch points during 360-degree base rotation.

### Step 3: Software Launch Configuration
No code changes, URDF recompilations, or configuration file edits are required.
Launch the system with the single argument:
```bash
ros2 launch ranger_bringup sim.launch.py manipulator:=true manipulator_type:=piper
# OR via Makefile:
make piper
```

### Step 4: Post-Installation Verification Checklist
Execute the verification suite to certify readiness:
- [ ] Run `./scripts/detect_manipulator.sh` — confirm detection of `piper`.
- [ ] Run `ros2 control list_controllers` — confirm `piper_arm_controller` is `active`.
- [ ] Inspect `/manipulator/status` — verify `"ready": true` and `"controller_active": true`.
- [ ] Run `python3 tests/verify_manipulator_modular.py piper` — confirm 100% check pass.

---

## Phase 2: Removing the Manipulator (Mobile Manipulator -> AMR)

### Step 1: De-energize and Park
1. If the robot is powered on, command the manipulator to its safe stowed configuration (`positions: [0, 0, 0, 0, 0, 0]`).
2. Engage the Emergency Stop switch. Turn the main key switch to OFF.

### Step 2: Disconnect Cabling
1. Unplug the 24V XT30/XT60 power connector.
2. Loosen thumbscrews and unplug the CAN communication cable. Cap both chassis bulkheads with protective dust caps.

### Step 3: Mechanical Detachment
1. Loosen and remove the 4x M5 bolts holding the arm base to the `manipulator_mount` plate.
2. Lift the manipulator arm assembly vertically off the deck and place it into its protective transport crate.
3. Install the flush protective rubber plate over the `manipulator_mount` pattern on the top deck.

### Step 4: Software Reconfiguration
Launch the robot in base-only AMR mode:
```bash
ros2 launch ranger_bringup sim.launch.py manipulator:=false manipulator_type:=none
# OR via Makefile:
make base-only
```

### Step 5: Post-Removal Cleanliness Audit
Run the automated reversion audit:
```bash
python3 tests/verify_manipulator_modular.py base_only
```
**Acceptance Criteria:**
- ZERO Piper joints or links in URDF or TF
- ZERO `piper_arm_controller` in `ros2 control list_controllers`
- ZERO MoveIt processes running
- Autonomous missions complete cleanly with physical grasp steps automatically bypassed.
