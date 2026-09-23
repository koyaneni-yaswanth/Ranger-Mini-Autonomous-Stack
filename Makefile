# AgileX Ranger Mini Autonomous Stack Platform Makefile
SHELL := /bin/bash
PROJECT_DIR := $(CURDIR)
WS_DIR := $(abspath $(PROJECT_DIR)/../ranger_mini_lyrical_2604_ws)

.PHONY: all build clean test sim slam nav real diagnostics health check jetson-check jetson-setup hw-health validate

all: build

check:
	@bash $(PROJECT_DIR)/scripts/check_environment.sh

build:
	@bash $(PROJECT_DIR)/scripts/build.sh

clean:
	@bash $(PROJECT_DIR)/scripts/clean.sh

test:
	@bash $(PROJECT_DIR)/scripts/test.sh

sim:
	@bash $(PROJECT_DIR)/scripts/run_sim.sh

slam:
	@bash $(PROJECT_DIR)/scripts/run_slam.sh

nav:
	@bash $(PROJECT_DIR)/scripts/run_nav.sh

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
