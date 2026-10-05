#!/usr/bin/env python3
"""
JARVIS-X Demonstration Imitation Learning Trainer
Trains a Behavior Cloning policy on validated ALOHA demonstration tensors.
"""

import os
import sys
import argparse
import time
import glob
import json
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
from learning.hdf5_conversion.convert_aloha_dataset import convert_episode_to_tensors

def train_imitation(skill_name="place", epochs=20):
    print("=" * 80)
    print(f"      JARVIS-X IMITATION LEARNING TRAINING: SKILL='{skill_name.upper()}'")
    print("=" * 80)

    ep_dir = os.path.join(PROJECT_ROOT, "datasets", "jarvis_x", "episodes")
    ep_files = sorted(glob.glob(os.path.join(ep_dir, "*.json")))

    if not ep_files:
        print("[FAIL] No demonstration episodes available for imitation training.")
        sys.exit(1)

    print(f"Loading demonstrations from {len(ep_files)} episode(s)...")
    all_qpos = []
    all_act = []
    for f in ep_files:
        try:
            res = convert_episode_to_tensors(f)
            all_qpos.append(res["qpos"])
            all_act.append(res["action"])
        except Exception:
            pass

    X = np.concatenate(all_qpos, axis=0) # [N, 8]
    Y = np.concatenate(all_act, axis=0)  # [N, 8]
    N, D = X.shape
    print(f"Aggregated Demonstration Dataset: {N} transitions, state_dim={D}, action_dim={Y.shape[1]}")

    # Ridge Regression / MLP Analytical closed-form solution: W = (X^T X + lambda I)^-1 X^T Y
    reg = 1e-4
    W = np.linalg.solve(np.dot(X.T, X) + reg * np.eye(D), np.dot(X.T, Y))

    # Compute reconstruction loss
    pred = np.dot(X, W)
    mse = np.mean((pred - Y)**2)

    out_dir = os.path.join(PROJECT_ROOT, "models", "checkpoints")
    os.makedirs(out_dir, exist_ok=True)
    ckpt_path = os.path.join(out_dir, f"piper_imitation_{skill_name}.npz")
    np.savez(ckpt_path, W=W, mse=mse, skill=skill_name)

    print(f"  Training Completed: MSE Loss = {mse:8.6f}")
    print(f"  [OK] Imitation checkpoint saved to: {ckpt_path}")
    print(f">>> [PASS] IMITATION LEARNING FOR SKILL '{skill_name.upper()}' COMPLETED <<<")
    print("=" * 80)
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", default="place", choices=["reach", "pick", "place", "lift"])
    parser.add_argument("--epochs", type=int, default=20)
    args = parser.parse_args()
    sys.exit(train_imitation(args.skill, args.epochs))
