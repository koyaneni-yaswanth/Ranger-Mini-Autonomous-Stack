# AgileX Ranger Mini Autonomous Stack Platform Makefile
SHELL := /bin/bash
PROJECT_DIR := $(CURDIR)
WS_DIR := $(abspath $(PROJECT_DIR)/../ranger_mini_lyrical_2604_ws)

.PHONY: all setup build clean stop test lint audit sim-base sim sim-debug demo sim-doctor simulation-e2e-test gazebo-failures-test sim-test navigation-test manipulation-test voice-test jarvis-test hardware-check hardware-test replay doctor base-only piper detect-manipulator slam nav rviz teleop real diagnostics health check jetson-check jetson-setup hw-health validate ai-task orchestrator cli jarvis gazebo isaac train run-all run-all-gui gui

all: build

# Master Simulation & Demonstration Commands (Prompt Section 3, 25, 26, 27, 30, 31)
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
