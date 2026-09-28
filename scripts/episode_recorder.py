#!/usr/bin/env python3
"""
JARVIS-X Episode Data Recorder
Captures live multimodal trajectories, state observations, actions,
and task verification verdicts into datasets/jarvis_x/.
"""

import os
import sys
import time
import json
import uuid
import datetime

class EpisodeRecorder:
    def __init__(self, dataset_dir="/home/yash/ranger_mini_lyrical_2604_project/datasets/jarvis_x"):
        self.dataset_dir = dataset_dir
        self.episodes_dir = os.path.join(dataset_dir, "episodes")
        os.makedirs(self.episodes_dir, exist_ok=True)
        self.current_episode = None
        self.start_time = None

    def start_episode(self, task_name="red_cube_pick_and_place", execution_mode="rl_policy", initial_conditions=None):
        ep_id = f"ep_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        self.start_time = time.time()
        self.current_episode = {
            "$schema": "https://agilex.ai/schemas/jarvis_x/episode_v1.json",
            "metadata": {
                "episode_id": ep_id,
                "timestamp_utc": datetime.datetime.utcnow().isoformat() + "Z",
                "task_name": task_name,
                "execution_mode": execution_mode,
                "robot_platform": "AgileX Ranger Mini v2 + Piper 6-DOF",
                "simulator": "Gazebo Harmonic / NVIDIA Isaac Sim 6.0"
            },
            "initial_conditions": initial_conditions or {
                "target_object": "red_cube",
                "target_spawn_xyz": [0.450, 0.000, 0.330],
                "table_surface_z": 0.300
            },
            "trajectory_stream": [],
            "verification_verdict": {}
        }
        return ep_id

    def record_step(self, obs: dict, action: dict, reward_dict: dict = None):
        if not self.current_episode:
            return
        t_elapsed = round(time.time() - self.start_time, 3)
        step_entry = {
            "step": len(self.current_episode["trajectory_stream"]),
            "time_from_start_s": t_elapsed,
            "observation": obs,
            "action": action,
            "reward_breakdown": reward_dict or {}
        }
        self.current_episode["trajectory_stream"].append(step_entry)

    def finish_episode(self, verdict: dict) -> str:
        if not self.current_episode:
            return ""

        verdict["execution_duration_s"] = round(time.time() - self.start_time, 2)
        self.current_episode["verification_verdict"] = verdict

        ep_id = self.current_episode["metadata"]["episode_id"]
        filepath = os.path.join(self.episodes_dir, f"{ep_id}.json")
        with open(filepath, 'w') as f:
            json.dump(self.current_episode, f, indent=2)

        # Update index.json
        index_path = os.path.join(self.dataset_dir, "index.json")
        index = {"total_episodes": 0, "successful_episodes": 0, "episodes": []}
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r') as f:
                    index = json.load(f)
            except Exception:
                pass

        index["episodes"].append({
            "episode_id": ep_id,
            "task_name": self.current_episode["metadata"]["task_name"],
            "status": verdict.get("status", "UNKNOWN"),
            "duration_s": verdict["execution_duration_s"],
            "timestamp": self.current_episode["metadata"]["timestamp_utc"]
        })
        index["total_episodes"] = len(index["episodes"])
        index["successful_episodes"] = sum(1 for e in index["episodes"] if e["status"] == "SUCCESS")

        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)

        print(f"[OK] Episode logged: {filepath}")
        self.current_episode = None
        return filepath

def main():
    print("=" * 80)
    print("    JARVIS-X EPISODE RECORDER SELF-TEST & VALIDATION")
    print("=" * 80)
    recorder = EpisodeRecorder()
    ep_id = recorder.start_episode(execution_mode="rl_policy_test")

    # Record synthetic trial steps
    for step in range(10):
        recorder.record_step(
            obs={"q": [0.0, 0.4 + step*0.01, 1.2 + step*0.02, 0.0, 0.2, 0.0], "dist_m": 0.25 - step*0.02},
            action={"delta_q": [0.0, 0.01, 0.02, 0.0, 0.0, 0.0], "gripper": -1.0},
            reward_dict={"r_dist": -0.25 + step*0.02, "total": -0.25 + step*0.02}
        )

    verdict = {
        "grasp_verified": True,
        "lift_verified": True,
        "final_height_m": 0.8466,
        "net_lift_m": 0.5166,
        "placement_verified": True,
        "status": "SUCCESS"
    }
    ep_path = recorder.finish_episode(verdict)

    assert os.path.exists(ep_path), "Recorded episode file missing!"
    print(">>> [PASS] EPISODE DATA RECORDER & DATASET LOGGING VERIFIED <<<")
    print("=" * 80)

if __name__ == '__main__':
    main()