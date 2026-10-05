#!/usr/bin/env python3
"""
JARVIS-X Capability Registry
Tracks the operational readiness and safety status of all robot skills:
AVAILABLE, DEGRADED, UNAVAILABLE, BUSY, UNSAFE.
"""

from enum import Enum
from typing import Dict, Any

class SkillStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    BUSY = "BUSY"
    UNSAFE = "UNSAFE"

class CapabilityRegistry:
    def __init__(self):
        self._skills: Dict[str, Dict[str, Any]] = {
            "ObserveScene": {"status": SkillStatus.AVAILABLE, "type": "perception"},
            "FindObject": {"status": SkillStatus.AVAILABLE, "type": "perception"},
            "SearchArea": {"status": SkillStatus.AVAILABLE, "type": "navigation"},
            "NavigateTo": {"status": SkillStatus.AVAILABLE, "type": "navigation"},
            "ApproachObject": {"status": SkillStatus.AVAILABLE, "type": "navigation"},
            "InspectObject": {"status": SkillStatus.AVAILABLE, "type": "perception"},
            "ReachPose": {"status": SkillStatus.AVAILABLE, "type": "manipulation"},
            "PickObject": {"status": SkillStatus.AVAILABLE, "type": "manipulation"},
            "VerifyGrasp": {"status": SkillStatus.AVAILABLE, "type": "perception"},
            "LiftObject": {"status": SkillStatus.AVAILABLE, "type": "manipulation"},
            "TransportObject": {"status": SkillStatus.AVAILABLE, "type": "composite"},
            "PlaceObject": {"status": SkillStatus.AVAILABLE, "type": "manipulation"},
            "VerifyPlacement": {"status": SkillStatus.AVAILABLE, "type": "perception"},
            "ReadText": {"status": SkillStatus.AVAILABLE, "type": "perception"},
            "ReadQRCode": {"status": SkillStatus.AVAILABLE, "type": "perception"},
            "RobotStatus": {"status": SkillStatus.AVAILABLE, "type": "diagnostic"},
            "Pause": {"status": SkillStatus.AVAILABLE, "type": "control"},
            "Resume": {"status": SkillStatus.AVAILABLE, "type": "control"},
            "Stop": {"status": SkillStatus.AVAILABLE, "type": "safety"},
            "AskUser": {"status": SkillStatus.AVAILABLE, "type": "interaction"},
            "Speak": {"status": SkillStatus.AVAILABLE, "type": "interaction"}
        }

    def get_status(self, skill_name: str) -> SkillStatus:
        if skill_name not in self._skills:
            return SkillStatus.UNAVAILABLE
        return self._skills[skill_name]["status"]

    def set_status(self, skill_name: str, status: SkillStatus):
        if skill_name in self._skills:
            self._skills[skill_name]["status"] = status

    def is_executable(self, skill_name: str) -> bool:
        return self.get_status(skill_name) in (SkillStatus.AVAILABLE, SkillStatus.DEGRADED)

    def audit_capabilities(self) -> Dict[str, str]:
        return {s: data["status"].value for s, data in self._skills.items()}

if __name__ == "__main__":
    reg = CapabilityRegistry()
    print("=== JARVIS-X CAPABILITY REGISTRY ===")
    for s, st in reg.audit_capabilities().items():
        print(f"  Skill: {s:20} -> Status: {st}")
