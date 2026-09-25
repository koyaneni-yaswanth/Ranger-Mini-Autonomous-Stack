import sys

ws_path = '/home/yash/ranger_mini_lyrical_2604_ws/install/ranger_missions/lib/python3.14/site-packages'
if ws_path not in sys.path:
    sys.path.insert(0, ws_path)

from ranger_missions.robot_abstraction import RobotAbstraction, BackendPlatform
from ranger_missions.skill_library import (
    LocateObjectSkill, ApproachTargetSkill, PickSkill,
    VerifyGraspSkill, TransportSkill, PlaceSkill,
    VerifyPlaceSkill, DockSkill, SkillStatus
)

class MockHAL:
    def __init__(self):
        self.cmd_history = []
        self.arm_history = []
        self.has_manipulator = True

    def send_base_velocity(self, vx, wz, vy=0.0):
        self.cmd_history.append((vx, wz, vy))

    def stop_base(self):
        self.cmd_history.append((0.0, 0.0, 0.0))

    def send_arm_pose(self, pose_name, duration_sec=2.0):
        self.arm_history.append((pose_name, duration_sec))
        return True

hal = MockHAL()
context = {
    "target_color": "red",
    "target_class": "cube",
    "destination_station": "target_station",
    "stations": {"target_station": {"coordinates": [1.6, -0.6, 0.40]}}
}

# 1. Test LocateObjectSkill
locate = LocateObjectSkill(hal)
r1 = locate.execute(context)
assert r1.is_success, f"LocateObjectSkill failed: {r1.message}"
print(f"[PASS] LocateObjectSkill: {r1.message} -> {r1.data}")

# 2. Test ApproachTargetSkill
approach = ApproachTargetSkill(hal)
r2 = approach.execute(context)
assert r2.is_success, f"ApproachTargetSkill failed: {r2.message}"
print(f"[PASS] ApproachTargetSkill: {r2.message}")

# 3. Test PickSkill
pick = PickSkill(hal)
r3 = pick.execute(context)
assert r3.is_success, f"PickSkill failed: {r3.message}"
print(f"[PASS] PickSkill: {r3.message}")

# 4. Test VerifyGraspSkill
verify_grasp = VerifyGraspSkill(hal)
r4 = verify_grasp.execute(context)
assert r4.is_success, f"VerifyGraspSkill failed: {r4.message}"
assert r4.data["status"] == "SUCCESS"
print(f"[PASS] VerifyGraspSkill: {r4.message} -> {r4.data}")

# 5. Test TransportSkill
transport = TransportSkill(hal)
r5 = transport.execute(context)
assert r5.is_success, f"TransportSkill failed: {r5.message}"
print(f"[PASS] TransportSkill: {r5.message}")

# 6. Test PlaceSkill & VerifyPlaceSkill
place = PlaceSkill(hal)
r6 = place.execute(context)
assert r6.is_success, f"PlaceSkill failed: {r6.message}"
print(f"[PASS] PlaceSkill: {r6.message}")

verify_place = VerifyPlaceSkill(hal)
r7 = verify_place.execute(context)
assert r7.is_success, f"VerifyPlaceSkill failed: {r7.message}"
print(f"[PASS] VerifyPlaceSkill: {r7.message}")

# 7. Test DockSkill
dock = DockSkill(hal)
r8 = dock.execute(context)
assert r8.is_success, f"DockSkill failed: {r8.message}"
print(f"[PASS] DockSkill: {r8.message}")

print("\nALL TASK / SKILL LAYER & ROBOT ABSTRACTION TESTS PASSED!")
