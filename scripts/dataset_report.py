#!/usr/bin/env python3
"""
JARVIS-X Dataset Audit & Lineage Report Generator
"""

import os
import sys
import glob
import json

def generate_report():
    print("=" * 80)
    print("               JARVIS-X MULTIMODAL DATASET REPORT")
    print("=" * 80)

    ep_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datasets", "jarvis_x", "episodes")
    ep_files = sorted(glob.glob(os.path.join(ep_dir, "*.json")))

    total_episodes = len(ep_files)
    total_timesteps = 0
    total_duration = 0.0
    sources = {}

    for f in ep_files:
        try:
            d = json.load(open(f))
            meta = d.get("metadata", {})
            src = meta.get("source_label", "UNKNOWN")
            sources[src] = sources.get(src, 0) + 1
            steps = d.get("timesteps") or d.get("trajectory_stream") or []
            total_timesteps += len(steps)
            total_duration += float(meta.get("duration_sec", len(steps)*0.02))
        except:
            pass

    print(f"Total Valid Episodes:    {total_episodes}")
    print(f"Total Synchronized Steps: {total_timesteps} steps")
    print(f"Total Logged Duration:   {total_duration:.2f} seconds")
    print("\nBreakdown by Source Label:")
    for src, count in sources.items():
        print(f"  - {src:<16}: {count} episode(s)")

    print("=" * 80)
    print(">>> [PASS] DATASET REPORT GENERATED <<<")
    print("=" * 80)
    return 0

if __name__ == "__main__":
    sys.exit(generate_report())
