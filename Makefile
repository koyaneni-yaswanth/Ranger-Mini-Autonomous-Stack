# AgileX Ranger Mini Autonomous Stack Platform Makefile
SHELL := /bin/bash
PROJECT_DIR := $(CURDIR)
WS_DIR := $(abspath $(PROJECT_DIR)/../ranger_mini_lyrical_2604_ws)

.PHONY: all build clean stop test sim base-only piper detect-manipulator slam nav rviz teleop real diagnostics health check jetson-check jetson-setup hw-health validate ai-task orchestrator cli

all: build

check:
	@bash $(PROJECT_DIR)/scripts/check_environment.sh

build:
	@bash $(PROJECT_DIR)/scripts/build.sh

clean:
	@bash $(PROJECT_DIR)/scripts/clean.sh

stop:
	@bash $(PROJECT_DIR)/scripts/stop.sh

test:
	@bash $(PROJECT_DIR)/scripts/test.sh

sim:
	@bash $(PROJECT_DIR)/scripts/run_sim.sh

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
