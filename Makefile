# AgileX Ranger Mini Autonomous Stack Platform Makefile
SHELL := /bin/bash
PROJECT_DIR := $(CURDIR)
ROS_ENV := source /env/source_lyrical.sh && export ROS_DOMAIN_ID=10 &&
WS_DIR := $(abspath $(PROJECT_DIR)/../ranger_mini_lyrical_2604_ws)

.PHONY: all setup build clean stop test lint audit sim-base sim sim-debug demo sim-doctor simulation-e2e-test gazebo-failures-test sim-test navigation-test manipulation-test voice-test jarvis-test hardware-check hardware-test replay doctor base-only piper detect-manipulator slam nav rviz teleop real diagnostics health check jetson-check jetson-setup hw-health validate ai-task orchestrator cli jarvis gazebo isaac train run-all run-all-gui gui piper-sim piper-doctor piper-test piper-ik-test piper-gripper-test piper-pick-test piper-place-test piper-regression-test cube-pick-test place-test perception-test grasp-test manipulation-doctor jarvis-doctor

all: build

# Master Simulation & Demonstration Commands (Prompt Section 3, 25, 26, 27, 30, 31)
piper-sim:
	@bash $(PROJECT_DIR)/scripts/run_piper_sim.sh

piper-doctor:
	@bash $(PROJECT_DIR)/scripts/piper_doctor.sh

piper-test:
	@source $(PROJECT_DIR)/env/source_lyrical.sh && export ROS_DOMAIN_ID=10 && python3 $(PROJECT_DIR)/scripts/test_piper_motion.py

piper-ik-test:
	@source $(PROJECT_DIR)/env/source_lyrical.sh && export ROS_DOMAIN_ID=10 && python3 $(PROJECT_DIR)/scripts/test_piper_ik.py

piper-gripper-test:
	@source $(PROJECT_DIR)/env/source_lyrical.sh && export ROS_DOMAIN_ID=10 && python3 $(PROJECT_DIR)/scripts/test_piper_gripper.py

piper-pick-test:
	@source $(PROJECT_DIR)/env/source_lyrical.sh && export ROS_DOMAIN_ID=10 && python3 $(PROJECT_DIR)/scripts/test_piper_pick.py

piper-place-test:
	@source $(PROJECT_DIR)/env/source_lyrical.sh && export ROS_DOMAIN_ID=10 && python3 $(PROJECT_DIR)/scripts/test_piper_place.py

piper-regression-test:
	@source $(PROJECT_DIR)/env/source_lyrical.sh && export ROS_DOMAIN_ID=10 && python3 $(PROJECT_DIR)/scripts/test_piper_regression.py

cube-pick-test:
	@source $(PROJECT_DIR)/env/source_lyrical.sh && export ROS_DOMAIN_ID=10 && python3 $(PROJECT_DIR)/scripts/test_cube_pick.py

place-test:
	@source $(PROJECT_DIR)/env/source_lyrical.sh && export ROS_DOMAIN_ID=10 && python3 $(PROJECT_DIR)/scripts/test_cube_place.py

perception-test:
	@source $(PROJECT_DIR)/env/source_lyrical.sh && export ROS_DOMAIN_ID=10 && python3 $(PROJECT_DIR)/scripts/test_perception_audit.py

grasp-test:
	@source $(PROJECT_DIR)/env/source_lyrical.sh && export ROS_DOMAIN_ID=10 && python3 $(PROJECT_DIR)/scripts/test_cube_pick.py

manipulation-doctor:
	@source $(PROJECT_DIR)/env/source_lyrical.sh && export ROS_DOMAIN_ID=10 && python3 $(PROJECT_DIR)/scripts/manipulation_doctor.py

jarvis-doctor:
	@bash $(PROJECT_DIR)/scripts/sim_doctor.sh

sim-base:
	@bash $(PROJECT_DIR)/scripts/run_sim_base.sh

sim-nav:
	@bash $(PROJECT_DIR)/scripts/run_sim_nav.sh

sim-manipulation:
	@bash $(PROJECT_DIR)/scripts/run_sim_manipulation.sh

sim-perception:
	@bash $(PROJECT_DIR)/scripts/run_sim_perception.sh

sim-full:
	@bash $(PROJECT_DIR)/scripts/run_sim_full.sh

performance-test:
	@python3 $(PROJECT_DIR)/scripts/run_performance_test.py

sim:
	@bash $(PROJECT_DIR)/scripts/run_sim_gui.sh

sim-debug:
	@bash $(PROJECT_DIR)/scripts/sim_debug.sh

demo:
	@bash $(PROJECT_DIR)/scripts/run_demo.sh

sim-doctor:
	@bash $(PROJECT_DIR)/scripts/sim_doctor.sh

simulation-e2e-test:
	@python3 $(PROJECT_DIR)/tests/test_simulation_e2e.py

gazebo-failures-test:
	@python3 $(PROJECT_DIR)/tests/test_gazebo_failures.py

# Platform Lifecycle Commands
setup:
	@bash $(PROJECT_DIR)/scripts/setup_jetson.sh

build:
	@bash $(PROJECT_DIR)/scripts/build.sh

clean:
	@bash $(PROJECT_DIR)/scripts/clean.sh

test:
	@bash $(PROJECT_DIR)/scripts/test.sh

lint:
	@bash $(PROJECT_DIR)/scripts/lint.sh

audit:
	@echo "=============================================================================="
	@echo " JARVIS-X FORENSIC REPOSITORY AUDIT"
	@echo "=============================================================================="
	@cat $(PROJECT_DIR)/docs/ARCHITECTURE_AUDIT.md
	@echo ""
	@cat $(PROJECT_DIR)/docs/HARDWARE_STATUS.md

doctor:
	@bash $(PROJECT_DIR)/scripts/doctor.sh

sim-test:
	@python3 $(PROJECT_DIR)/tests/test_skills_and_hal.py

navigation-test:
	@python3 $(PROJECT_DIR)/tests/test_costmap_bounds_regression.py

manipulation-test:
	@python3 $(PROJECT_DIR)/tests/test_skills_and_hal.py

voice-test:
	@python3 $(PROJECT_DIR)/tests/test_voice_system.py

jarvis-test:
	@python3 $(PROJECT_DIR)/tests/test_section_69_matrix.py

hardware-check:
	@bash $(PROJECT_DIR)/scripts/hardware_health_check.sh

hardware-test:
	@bash $(PROJECT_DIR)/scripts/check_hardware.sh

replay:
	@echo "Replaying latest recorded mission rosbag2..."
	@if [ -d "$(PROJECT_DIR)/rosbag2" ]; then ros2 bag play $(PROJECT_DIR)/rosbag2; else echo "No active rosbag2 directory found. Launching synthetic replay test..."; python3 $(PROJECT_DIR)/scripts/run_winning_demos.py; fi

# Operational & Component Commands
check:
	@bash $(PROJECT_DIR)/scripts/check_environment.sh

stop:
	@bash $(PROJECT_DIR)/scripts/stop.sh

base-only:
	@bash $(PROJECT_DIR)/scripts/run_base_only.sh

piper:
	@bash $(PROJECT_DIR)/scripts/run_piper.sh

detect-manipulator:
	@bash $(PROJECT_DIR)/scripts/detect_manipulator.sh

slam:
	@bash $(PROJECT_DIR)/scripts/run_slam.sh

nav:
	@bash $(PROJECT_DIR)/scripts/run_nav.sh

rviz:
	@bash $(PROJECT_DIR)/scripts/run_rviz.sh

teleop:
	@bash $(PROJECT_DIR)/scripts/run_teleop.sh

real:
	@bash $(PROJECT_DIR)/scripts/run_real.sh

diagnostics:
	@bash $(PROJECT_DIR)/scripts/collect_diagnostics.sh

health:
	@bash $(PROJECT_DIR)/scripts/health_check.sh

jetson-check:
	@bash $(PROJECT_DIR)/scripts/check_jetson_environment.sh

jetson-setup:
	@bash $(PROJECT_DIR)/scripts/setup_jetson.sh

hw-health:
	@bash $(PROJECT_DIR)/scripts/hardware_health_check.sh

validate:
	@bash $(PROJECT_DIR)/scripts/validate_deployment.sh

ai-task:
	@source /opt/ros/lyrical/setup.bash && source $(WS_DIR)/install/setup.bash && ros2 run ranger_missions ai_task_interpreter

orchestrator:
	@source /opt/ros/lyrical/setup.bash && source $(WS_DIR)/install/setup.bash && ros2 run ranger_missions autonomous_task_orchestrator

cli:
	@source /opt/ros/lyrical/setup.bash && source $(WS_DIR)/install/setup.bash && python3 $(PROJECT_DIR)/scripts/interactive_task_cli.py

run-all:
	@bash $(PROJECT_DIR)/scripts/run_all.sh

run-all-gui:
	@GUI=true bash $(PROJECT_DIR)/scripts/run_all.sh

gui:
	@GUI=true bash $(PROJECT_DIR)/scripts/run_all.sh

jarvis:
	@bash $(PROJECT_DIR)/scripts/run_jarvis.sh

gazebo:
	@bash $(PROJECT_DIR)/scripts/run_gazebo.sh

isaac:
	@bash $(PROJECT_DIR)/scripts/run_isaac.sh

train:
	@bash $(PROJECT_DIR)/scripts/train.sh

# ----------------------------------------------------------------------------
# JARVIS-X Reinforcement Learning, Isaac Simulation & Sim-to-Real Targets
# ----------------------------------------------------------------------------

isaac-audit:
	@source $(PROJECT_DIR)/env/source_lyrical.sh && python3 $(PROJECT_DIR)/scripts/isaac_baseline_audit.py

isaac-validate-assets:
	@source $(PROJECT_DIR)/env/source_lyrical.sh && python3 $(PROJECT_DIR)/scripts/validate_isaac_assets.py

isaac-train:
	@mkdir -p /mnt/wsl/ranger_project && rsync -av --exclude 'build' --exclude 'log' --exclude '.git' $(PROJECT_DIR)/ /mnt/wsl/ranger_project/
	@wsl.exe -d Ubuntu-22.04 docker run --rm --gpus all -e ACCEPT_EULA=Y -v /mnt/wsl/ranger_project:/workspace --entrypoint /isaac-sim/python.sh nvcr.io/nvidia/isaac-sim:6.0.0-dev2 /workspace/scripts/train_piper_rl.py
	@cp -r /mnt/wsl/ranger_project/models/checkpoints/* $(PROJECT_DIR)/models/checkpoints/

isaac-eval:
	@mkdir -p /mnt/wsl/ranger_project && rsync -av --exclude 'build' --exclude 'log' --exclude '.git' $(PROJECT_DIR)/ /mnt/wsl/ranger_project/
	@wsl.exe -d Ubuntu-22.04 docker run --rm --gpus all -e ACCEPT_EULA=Y -v /mnt/wsl/ranger_project:/workspace --entrypoint /isaac-sim/python.sh nvcr.io/nvidia/isaac-sim:6.0.0-dev2 /workspace/scripts/evaluate_piper_policy.py
	@cp /mnt/wsl/ranger_project/docs/policy_evaluation_report.md $(PROJECT_DIR)/docs/

isaac-export:
	@mkdir -p /mnt/wsl/ranger_project && rsync -av --exclude 'build' --exclude 'log' --exclude '.git' $(PROJECT_DIR)/ /mnt/wsl/ranger_project/
	@wsl.exe -d Ubuntu-22.04 docker run --rm --gpus all -e ACCEPT_EULA=Y -e PYTHONPATH=/workspace/.local_pip:/workspace -v /mnt/wsl/ranger_project:/workspace --entrypoint /isaac-sim/python.sh nvcr.io/nvidia/isaac-sim:6.0.0-dev2 /workspace/scripts/export_piper_policy.py
	@cp -r /mnt/wsl/ranger_project/models/exported/* $(PROJECT_DIR)/models/exported/

jarvis-rl-test:
	@source $(PROJECT_DIR)/env/source_lyrical.sh && export ROS_DOMAIN_ID=10 && python3 $(PROJECT_DIR)/scripts/test_jarvis_rl_mission.py

jarvis-e2e-all: isaac-audit isaac-validate-assets jarvis-rl-test
	@echo ">>> [PASS] ALL JARVIS-X REINFORCEMENT LEARNING & MISSION HARNESSES VERIFIED <<<"
