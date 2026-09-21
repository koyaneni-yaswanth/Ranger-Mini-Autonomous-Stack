cmake_minimum_required(VERSION 3.8)
project(ranger_tests)

find_package(ament_cmake REQUIRED)

install(DIRECTORY scripts
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
