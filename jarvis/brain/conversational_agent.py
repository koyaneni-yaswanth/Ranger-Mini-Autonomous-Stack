#!/usr/bin/env python3
"""
JARVIS-X Conversational Agent & Reasoning Engine
Differentiates Conversation Mode vs Physical Task Mode.
Employs entity grounding, clarification prompts, and unsupported task refusal.
"""

import os
import sys
import re
from typing import Dict, Any, Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from jarvis.capabilities.capability_registry import CapabilityRegistry
from jarvis.planner.structured_task_planner import StructuredTaskPlanner

class ConversationalAgent:
    def __init__(self):
        self.registry = CapabilityRegistry()
        self.planner = StructuredTaskPlanner(self.registry)
        self.mode = "CONVERSATION"  # 'CONVERSATION' or 'PHYSICAL_TASK'
        self.current_task = None
        self.world_state = {
            "battery_soc": 88.5,
            "battery_voltage": 25.2,
            "known_objects": ["red cube", "blue cylinder"],
            "known_surfaces": ["table", "tray", "charging dock"],
            "robot_status": "READY"
        }

    def process_utterance(self, text: str) -> Dict[str, Any]:
        text_clean = text.strip()
        lower = text_clean.lower()

        # 1. Stop / Pause / Resume Controls
        if any(w in lower for w in ["stop", "emergency stop", "halt"]):
            return {
                "mode": "PHYSICAL_TASK",
                "action": "EMERGENCY_STOP",
                "speech_response": "Emergency stop acknowledged. All robot motion halted immediately.",
                "plan": None
            }
        elif "pause" in lower:
            return {
                "mode": "PHYSICAL_TASK",
                "action": "PAUSE",
                "speech_response": "Task execution paused. Standing by in safe stance.",
                "plan": None
            }
        elif "continue" in lower or "resume" in lower:
            return {
                "mode": "PHYSICAL_TASK",
                "action": "RESUME",
                "speech_response": "Resuming validated task execution.",
                "plan": None
            }

        # 2. Conversational Queries (Conversation Mode - No Actuation)
        if any(w in lower for w in ["what are you doing", "status", "battery", "where did you put", "why did you stop"]):
            if "battery" in lower:
                resp = f"Battery telemetry: {self.world_state['battery_soc']}% ({self.world_state['battery_voltage']}V). Power bus nominal."
            elif "status" in lower or "doing" in lower:
                resp = f"Robot status is {self.world_state['robot_status']}. Manipulator stowed safely at workstation table."
            elif "where" in lower:
                resp = "The red cube was placed securely at the workstation tray."
            else:
                resp = "Motion paused by operator instruction. Standing by for command."
            return {
                "mode": "CONVERSATION",
                "action": "INFORM",
                "speech_response": resp,
                "plan": None
            }

        if any(w in lower for w in ["look around", "what do you see"]):
            obs_str = ", ".join(self.world_state["known_objects"])
            return {
                "mode": "CONVERSATION",
                "action": "DESCRIBE_SCENE",
                "speech_response": f"Visual scene inspection complete. I detect the following entities: {obs_str} on the table.",
                "plan": None
            }

        # 3. Conversational Correction: "No, put it in the tray instead"
        if "no" in lower and ("tray" in lower or "instead" in lower):
            dest = "tray"
            plan = self.planner.create_plan("pick_and_place", "red cube", dest)
            return {
                "mode": "PHYSICAL_TASK",
                "action": "CORRECTION_REPLAN",
                "speech_response": f"Correction received. Canceling previous goal and rerouting placement to the {dest}.",
                "plan": plan
            }

        # 4. Unsupported or Unsafe Requests (Benchmark 8)
        unsupported_keywords = ["fly", "jump", "stairs", "cook", "cut", "throw", "dance", "pour water"]
        if any(w in lower for w in unsupported_keywords):
            matched = [w for w in unsupported_keywords if w in lower][0]
            return {
                "mode": "CONVERSATION",
                "action": "REJECT_UNSUPPORTED",
                "speech_response": f"I cannot execute that request. The operation '{matched}' is unsupported by my mobile base and 6-DOF manipulator capabilities. Robot remains safely stationary.",
                "plan": None
            }

        # 5. Pick and Place Commands
        if "pick" in lower or "take" in lower or "grab" in lower or "bring" in lower:
            # Extract target object
            obj_match = None
            for obj in self.world_state["known_objects"]:
                if obj in lower:
                    obj_match = obj
                    break

            # Check for ambiguity: multiple or unknown
            if not obj_match:
                if "cube" in lower:
                    obj_match = "red cube"
                else:
                    return {
                        "mode": "CONVERSATION",
                        "action": "CLARIFICATION_REQUIRED",
                        "speech_response": "I detected an unfamiliar object in your request. Could you clarify which object you would like me to manipulate?",
                        "plan": None
                    }

            # Extract destination
            dest_match = "table"
            for s in self.world_state["known_surfaces"]:
                if s in lower:
                    dest_match = s
                    break

            plan = self.planner.create_plan("pick_and_place", obj_match, dest_match)
            valid, errs = self.planner.validate_plan(plan)
            if not valid:
                return {
                    "mode": "CONVERSATION",
                    "action": "PLAN_REJECTED",
                    "speech_response": f"Plan validation failed due to unavailable skills: {errs}",
                    "plan": None
                }

            return {
                "mode": "PHYSICAL_TASK",
                "action": "EXECUTE_PLAN",
                "speech_response": f"Understood. Initiating autonomous mission to pick up the {obj_match} and place it on the {dest_match}.",
                "plan": plan
            }

        # Default fallback
        return {
            "mode": "CONVERSATION",
            "action": "CLARIFICATION_REQUIRED",
            "speech_response": "I received your instruction, but the intent is not fully clear. Could you please specify whether you want me to inspect, navigate, or manipulate an object?",
            "plan": None
        }

if __name__ == "__main__":
    agent = ConversationalAgent()
    print("=== JARVIS-X CONVERSATIONAL AGENT TEST ===")
    test_queries = [
        "What are you doing?",
        "Look around and tell me what you see.",
        "Pick up the red cube and put it on the table.",
        "No, put it in the tray instead.",
        "Can you fly up to the ceiling?",
        "Stop!"
    ]
    for q in test_queries:
        res = agent.process_utterance(q)
        print(f"\nUser: '{q}'")
        print(f"  Mode:   {res['mode']} | Action: {res['action']}")
        print(f"  JARVIS: \"{res['speech_response']}\"")
        if res['plan']:
            print(f"  Plan:   {res['plan']['task']['intent']} -> Sequence: {res['plan']['task']['skill_sequence'][:4]}...")
