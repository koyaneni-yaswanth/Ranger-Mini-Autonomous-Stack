# Gazebo Simulation Infrastructure

- **Engine**: Gazebo Sim 6.18.0 (Fortress / Jetty protocol).
- **Physics**: DART engine with 1ms step size.
- **Render Engine**: OGRE 1.x (`<render_engine>ogre</render_engine>`) solving the OGRE-Next 2.2.5 texture copy exception.
- **Worlds**: 7 deterministic environments (`basic_test`, `indoor`, `warehouse`, `dynamic_obstacle`, `manipulation`, `failure_test`, `narrow_corridor`).
