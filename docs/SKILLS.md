# Composable Skill Library & Registry

## 1. Skill Definitions
Every capability is packaged as a reusable, decoupled skill conforming to `SkillBase`:
- `LocateObjectSkill` (Perception & 3D backprojection)
- `ApproachTargetSkill` (Visual standoff positioning)
- `PickSkill` (MoveIt 2 6-DOF grasp trajectory)
- `VerifyGraspSkill` (Multi-stage evaluation)
- `TransportSkill` (Compact transport posture)
- `NavigateToStationSkill` (Nav2 path planning & navigation)
- `PlaceSkill` (Surface descent and release)
- `VerifyPlaceSkill` (Clearance confirmation)
- `DockSkill` (Autonomous charging dock entry)
- `FollowPersonSkill` (Human tracking and safe following)
- `LearnedGraspSkill` (Isaac Lab reinforcement learning policy interface)
