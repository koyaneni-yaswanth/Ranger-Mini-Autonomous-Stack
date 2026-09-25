# Isaac Lab Task Specification: Autonomous Red Cube Pick & Place
class PickRedObjectTask:
    """
    Markov Decision Process (MDP) specification for learning 6-DOF grasping with domain randomization.
    """
    def __init__(self):
        self.object_class = "cube"
        self.object_color = "red"
        self.dimensions_m = [0.06, 0.06, 0.06]
        self.mass_range_kg = [0.10, 0.25]
        self.table_height_m = 0.45

        # Domain Randomization Parameters
        self.domain_randomization = {
            "friction_coefficient": [0.4, 0.9],
            "camera_rgb_noise_std": 0.02,
            "depth_noise_std_m": 0.005,
            "lighting_intensity": [0.7, 1.3]
        }

    def compute_reward(self, ee_pos, obj_pos, is_grasped, is_lifted):
        dist = np.linalg.norm(ee_pos - obj_pos)
        reward = -dist
        if is_grasped:
            reward += 5.0
        if is_lifted:
            reward += 10.0
        return reward
