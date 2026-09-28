"""
JARVIS-X RL Environment: AgileX Ranger Mini + Piper 6-DOF Manipulator
High-throughput vectorized PyTorch simulation environment supporting both GPU (CUDA) and CPU.
Computes batched analytical forward kinematics, grasp contacts, and physical lifting.
"""

import torch
import numpy as np
from isaac_lab.tasks.pick_red_object import PickRedObjectTask

class RangerMiniPiperEnv:
    def __init__(self, num_envs=64, device=None, seed=42):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        torch.manual_seed(seed)
        self.num_envs = num_envs
        self.dt = 0.02  # 50 Hz control loop
        self.obs_space_dim = 24
        self.action_space_dim = 7  # 6 arm joint deltas + 1 gripper command

        self.task = PickRedObjectTask(device=self.device)

        # Joint Limits (Piper 6-DOF)
        self.q_min = torch.tensor([-3.14, -1.57, -2.00, -3.14, -1.57, -3.14], device=self.device)
        self.q_max = torch.tensor([ 3.14,  1.57,  2.00,  3.14,  1.57,  3.14], device=self.device)
        self.max_delta_q = 0.04  # Max joint angle displacement per step (rad)

        # Home / Ready Pose for Arm
        self.home_q = torch.tensor([0.0, 0.40, 1.20, 0.0, 0.20, 0.0], device=self.device)

        # Base Offset on Ranger Mini top platform
        self.base_offset = torch.tensor([0.10, 0.0, 0.22], device=self.device)

        # State Tensors
        self.joint_pos = torch.zeros((num_envs, 6), device=self.device)
        self.joint_vel = torch.zeros((num_envs, 6), device=self.device)
        self.gripper_state = torch.zeros((num_envs, 2), device=self.device)  # Finger positions (m)
        self.cube_pos = torch.zeros((num_envs, 3), device=self.device)
        self.target_pos = torch.zeros((num_envs, 3), device=self.device)
        self.is_grasped = torch.zeros(num_envs, dtype=torch.bool, device=self.device)
        self.step_count = torch.zeros(num_envs, dtype=torch.long, device=self.device)

        self.reset()

    def compute_forward_kinematics(self, q):
        """
        Batched Forward Kinematics for Piper 6-DOF arm mounted on Ranger Mini.
        Returns end-effector position [N, 3] and approximate quaternion [N, 4].
        """
        N = q.shape[0]
        device = self.device

        def rot_z(angle):
            c = torch.cos(angle)
            s = torch.sin(angle)
            R = torch.zeros(N, 4, 4, device=device)
            R[:, 0, 0] = c
            R[:, 0, 1] = -s
            R[:, 1, 0] = s
            R[:, 1, 1] = c
            R[:, 2, 2] = 1.0
            R[:, 3, 3] = 1.0
            return R

        def rot_y(angle):
            c = torch.cos(angle)
            s = torch.sin(angle)
            R = torch.zeros(N, 4, 4, device=device)
            R[:, 0, 0] = c
            R[:, 0, 2] = s
            R[:, 1, 1] = 1.0
            R[:, 2, 0] = -s
            R[:, 2, 2] = c
            R[:, 3, 3] = 1.0
            return R

        def trans(xyz):
            T = torch.eye(4, device=device).unsqueeze(0).repeat(N, 1, 1)
            T[:, 0, 3] = xyz[0]
            T[:, 1, 3] = xyz[1]
            T[:, 2, 3] = xyz[2]
            return T

        T = trans(self.base_offset)
        T = T @ trans([0.0, 0.0, 0.06]) @ rot_z(q[:, 0])
        T = T @ trans([0.0, 0.0, 0.10]) @ rot_y(q[:, 1])
        T = T @ trans([0.0, 0.0, 0.30]) @ rot_y(q[:, 2])
        T = T @ trans([0.0, 0.0, 0.20]) @ rot_z(q[:, 3])
        T = T @ trans([0.0, 0.0, 0.10]) @ rot_y(q[:, 4])
        T = T @ trans([0.0, 0.0, 0.08]) @ rot_z(q[:, 5])
        T = T @ trans([0.0, 0.0, 0.04])  # Tool center point (TCP)

        ee_pos = T[:, :3, 3]
        # End-effector orientation quaternion (nominal downward pointing [0, 1, 0, 0])
        ee_quat = torch.zeros((N, 4), device=device)
        ee_quat[:, 1] = 1.0  # Normalized orientation
        return ee_pos, ee_quat

    def _get_obs(self):
        ee_pos, ee_quat = self.compute_forward_kinematics(self.joint_pos)
        # Add slight observation noise (sim-to-real domain randomization)
        pos_noise = torch.randn_like(self.joint_pos) * 0.002
        obs = torch.cat([
            self.joint_pos + pos_noise,      # 6
            self.joint_vel,                  # 6
            ee_pos,                          # 3
            ee_quat,                         # 4
            self.target_pos,                 # 3
            self.gripper_state               # 2
        ], dim=-1)                           # Total = 24
        return obs

    def reset(self, env_ids=None):
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)

        n = len(env_ids)
        # Randomize initial joints around ready pose
        noise = (torch.rand((n, 6), device=self.device) - 0.5) * 0.10
        self.joint_pos[env_ids] = torch.clamp(self.home_q.unsqueeze(0) + noise, self.q_min, self.q_max)
        self.joint_vel[env_ids] = 0.0

        # Randomize Cube Target Position on Workstation Table
        tx = 0.44 + (torch.rand(n, device=self.device) - 0.5) * 0.08
        ty = (torch.rand(n, device=self.device) - 0.5) * 0.14
        tz = torch.full((n,), 0.33, device=self.device)
        self.target_pos[env_ids, 0] = tx
        self.target_pos[env_ids, 1] = ty
        self.target_pos[env_ids, 2] = tz

        # Initial cube position matches spawn target
        self.cube_pos[env_ids] = self.target_pos[env_ids].clone()

        # Open Gripper (stroke = 0.035m)
        self.gripper_state[env_ids, 0] = 0.035
        self.gripper_state[env_ids, 1] = 0.035
        self.is_grasped[env_ids] = False
        self.step_count[env_ids] = 0

        return self._get_obs()

    def step(self, actions):
        """
        Executes one physics & control step across all parallel environments.
        actions: [N, 7] in range [-1.0, 1.0]
        """
        if not isinstance(actions, torch.Tensor):
            actions = torch.tensor(actions, dtype=torch.float32, device=self.device)

        actions = torch.clamp(actions, -1.0, 1.0)
        arm_actions = actions[:, :6]
        gripper_action = actions[:, 6]

        # Calculate joint deltas
        delta_q = arm_actions * self.max_delta_q
        prev_q = self.joint_pos.clone()

        # Update joints with clamping
        self.joint_pos = torch.clamp(self.joint_pos + delta_q, self.q_min, self.q_max)
        self.joint_vel = (self.joint_pos - prev_q) / self.dt
        self.step_count += 1

        # Gripper actuation: > 0 closes, < 0 opens
        closing = gripper_action > 0.0
        self.gripper_state[:, 0] = torch.where(closing, torch.tensor(0.005, device=self.device), torch.tensor(0.035, device=self.device))
        self.gripper_state[:, 1] = self.gripper_state[:, 0]

        # Kinematics & Contact Detection
        ee_pos, ee_quat = self.compute_forward_kinematics(self.joint_pos)
        dist_to_cube = torch.norm(ee_pos - self.cube_pos, dim=-1)

        # Grasp condition: close proximity (< 4.5cm) AND closing gripper
        can_grasp = (dist_to_cube < 0.045) & closing
        self.is_grasped = self.is_grasped | can_grasp

        # Release condition: gripper opens
        can_release = gripper_action < -0.2
        self.is_grasped = self.is_grasped & (~can_release)

        # If grasped, cube tracks end-effector with fixed grasp offset
        for i in range(self.num_envs):
            if self.is_grasped[i]:
                self.cube_pos[i] = ee_pos[i]
            else:
                # Sits on table surface if not grasped
                self.cube_pos[i, 2] = torch.clamp(self.cube_pos[i, 2] - 9.81 * (self.dt ** 2), min=self.task.table_height + 0.025)

        # Check lift verification: vertical delta z >= 8cm
        lift_height = self.cube_pos[:, 2] - self.task.table_height
        is_lifted = self.is_grasped & (lift_height >= self.task.lift_threshold)

        # Success condition
        success = is_lifted

        # Compute batched reward
        rewards, r_breakdown = self.task.compute_reward(
            ee_pos=ee_pos,
            target_pos=self.target_pos,
            cube_pos=self.cube_pos,
            actions=actions,
            joint_vels=self.joint_vel,
            is_grasped=self.is_grasped,
            is_lifted=is_lifted,
            success=success
        )

        # Termination: success or max steps
        dones = success | (self.step_count >= self.task.max_episode_steps)

        # Auto-reset terminated environments
        if torch.any(dones):
            reset_ids = torch.nonzero(dones).squeeze(-1)
            self.reset(reset_ids)

        obs = self._get_obs()
        infos = {
            "success_rate": success.float().mean().item(),
            "mean_dist": dist_to_cube.mean().item(),
            "reward_breakdown": r_breakdown
        }
        return obs, rewards, dones, infos