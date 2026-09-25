# Isaac Lab Simulation Environment for AgileX Ranger Mini + Piper 6-DOF
import numpy as np

class RangerMiniPiperEnv:
    """
    Gym-compatible reinforcement learning environment for mobile manipulation in Isaac Sim.
    """
    def __init__(self, num_envs=64, headless=True):
        self.num_envs = num_envs
        self.headless = headless
        self.action_space_dim = 6  # 6 arm joint delta commands
        self.obs_space_dim = 24    # 6 arm joints + 6 velocities + 3 obj pos + 3 target pos + 6 robot state

    def reset(self):
        obs = np.zeros((self.num_envs, self.obs_space_dim), dtype=np.float32)
        return obs

    def step(self, actions):
        actions = np.clip(actions, -1.0, 1.0)
        obs = np.zeros((self.num_envs, self.obs_space_dim), dtype=np.float32)
        rewards = np.ones((self.num_envs,), dtype=np.float32)
        dones = np.zeros((self.num_envs,), dtype=bool)
        infos = {}
        return obs, rewards, dones, infos
