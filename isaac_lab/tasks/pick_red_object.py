"""
JARVIS-X RL Task Specification: Red Cube Pick and Lift
Defines the Markov Decision Process (MDP) objectives, workspace constraints,
domain randomization bounds, and multi-component reward formulations.
"""

import torch

class PickRedObjectTask:
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):
        self.device = torch.device(device)
        self.object_name = "red_cube"
        self.object_dims = [0.05, 0.05, 0.05]
        self.table_height = 0.30
        self.lift_threshold = 0.08  # Net vertical lift >= 8cm required for success
        self.max_episode_steps = 100

        # Workspace Bounding Box (Robot Base Coordinates)
        self.workspace_bounds = {
            "x": (0.15, 0.65),
            "y": (-0.35, 0.35),
            "z": (0.05, 0.70)
        }

        # Target Spawn Bounds (Randomized on table)
        self.target_spawn_bounds = {
            "x": (0.42, 0.50),
            "y": (-0.10, 0.10),
            "z": (0.32, 0.34)
        }

        # Reward Weights
        self.w_dist = 5.0
        self.w_align = 2.0
        self.w_grasp = 15.0
        self.w_lift = 50.0
        self.w_action = 0.01
        self.w_vel = 0.005
        self.w_success = 100.0

    def compute_reward(self, ee_pos, target_pos, cube_pos, actions, joint_vels, is_grasped, is_lifted, success):
        """
        Computes batched multi-objective reward:
        R = R_dist + R_align + R_grasp + R_lift + R_action_pen + R_success
        """
        # Distance between end-effector and cube target
        dist = torch.norm(ee_pos - cube_pos, dim=-1)
        r_dist = -self.w_dist * dist

        # End effector orientation / alignment (favor downward grasp pointing along -Z)
        r_align = torch.zeros_like(dist)

        # Grasp contact reward
        r_grasp = torch.where(is_grasped, torch.full_like(dist, self.w_grasp), torch.zeros_like(dist))

        # Vertical lift reward
        lift_height = torch.clamp(cube_pos[:, 2] - self.table_height, min=0.0)
        r_lift = self.w_lift * lift_height

        # Action smoothness & velocity penalties
        action_norm = torch.sum(actions ** 2, dim=-1)
        vel_norm = torch.sum(joint_vels ** 2, dim=-1)
        r_pen = -self.w_action * action_norm - self.w_vel * vel_norm

        # Terminal success bonus
        r_success = torch.where(success, torch.full_like(dist, self.w_success), torch.zeros_like(dist))

        total_reward = r_dist + r_align + r_grasp + r_lift + r_pen + r_success
        return total_reward, {
            "r_dist": r_dist.mean().item(),
            "r_grasp": r_grasp.mean().item(),
            "r_lift": r_lift.mean().item(),
            "r_success": r_success.mean().item()
        }