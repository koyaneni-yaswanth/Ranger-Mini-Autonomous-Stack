#!/bin/bash
set -e

echo "Installing ROS 2 Lyrical Environment (via Docker)......"

DOCKER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../docker/lyrical"

echo "Building Lyrical Docker Image..."
cd "$DOCKER_DIR"
docker build -t ros2_lyrical_desktop .

echo "Lyrical Image built successfully."
echo "Run with: docker run -it --rm --net=host -v \"$HOME/robotics_platform:/root/robotics_platform\" ros2_lyrical_desktop"
