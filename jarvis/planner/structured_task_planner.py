import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
#!/usr/bin/env python3
"""
JARVIS-X Structured Task Planner
Translates grounded intent into a constrained schema plan with capability audits.
Does not emit direct actuator commands.
"""

from typing import Dict, Any, List, Optional
from jarvis.capabilities.capability_registry import CapabilityRegistry, SkillStatus

class StructuredTaskPlanner:
    def __init__(self, registry: Optional[CapabilityRegistry] = None):
        self.registry = registry or CapabilityRegistry()

    def create_plan(self, intent: str, object_query: str, destination: Optional[str] = None, extra_constraints: Optional[Dict] = None) -> Dict[str, Any]:
        plan = {
            "task": {
                "intent": intent,
                "object": {
                    "query": object_query,
                    "category": self._classify_entity(object_query)
                },
                "destination": {
                    "query": destination or "default_workstation",
                    "category": self._classify_entity(destination or "table")
                },
                "constraints": {
                    "require_confirmation_if_ambiguous": True,
                    "require_verified_grasp": True,
                    "require_verified_placement": True,
                    "max_velocity_scaling": 0.5
                },
                "skill_sequence": []
            }
        }
        if extra_constraints:
            plan["task"]["constraints"].update(extra_constraints)

        # Decompose intent into skill sequence
        skills = self._decompose_intent(intent)
        plan["task"]["skill_sequence"] = skills
        return plan

    def validate_plan(self, plan: Dict[str, Any]):
        errors = []
        skills = plan.get("task", {}).get("skill_sequence", [])
        if not skills:
            errors.append("Empty skill sequence")

        for skill in skills:
            status = self.registry.get_status(skill)
            if status not in (SkillStatus.AVAILABLE, SkillStatus.DEGRADED):
                errors.append(f"Required skill '{skill}' is {status.value}")

        return len(errors) == 0, errors

    def _classify_entity(self, query: str) -> str:
        q = query.lower()
        if any(w in q for w in ["cube", "box", "cylinder", "bottle", "can"]):
            return "Object"
        elif any(w in q for w in ["table", "shelf", "counter", "tray"]):
            return "Surface"
        elif any(w in q for w in ["bin", "box", "basket"]):
            return "Container"
        elif any(w in q for w in ["charging", "station", "room"]):
            return "Location"
        elif any(w in q for w in ["person", "human", "operator"]):
            return "Person"
        return "UnknownEntity"

    def _decompose_intent(self, intent: str) -> List[str]:
        if intent == "pick_and_place":
            return [
                "FindObject", "ApproachObject", "ReachPose",
                "PickObject", "VerifyGrasp", "TransportObject",
                "PlaceObject", "VerifyPlacement"
            ]
        elif intent == "inspect":
            return ["FindObject", "ApproachObject", "InspectObject", "Speak"]
        elif intent == "stop":
            return ["Stop"]
        elif intent == "status":
            return ["RobotStatus", "Speak"]
        else:
            return ["AskUser"]

if __name__ == "__main__":
    planner = StructuredTaskPlanner()
    plan = planner.create_plan("pick_and_place", "red cube", "target tray")
    valid, errs = planner.validate_plan(plan)
    print("Structured Plan Generated:")
    import json
    print(json.dumps(plan, indent=2))
    status_str = "VALID" if valid else f"INVALID (Errors: {errs})"
    print(f"Validation Status: {status_str}")
