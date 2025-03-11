from typing import Optional

import numpy as np
import gymnasium as gym


class IntersectionEnv(gym.Env):
    def __init__(self):
        self._yellow_duration = 3
        self._passed_cars = 0

        self._pressure = np.array([0, 0, 0, 0], dtype=np.int32)
        self._nearest = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        self._current_light = 0

        self.observation_space = gym.spaces.Dict(
            {
                "pressure": gym.spaces.Box(low=0, high=50, shape=(4,), dtype=np.int32),
                "nearest": gym.spaces.Box(low=0, high=1, shap=(4,), dtype=np.float32),
            }
        )
        self.action_space = gym.spaces.Discrete(2)

    def _get_obs(self):
        return {"pressure": self._pressure, "nearest": self._nearest}

    def _get_info(self):
        return {"idle_cars": [pressure if nearest == 0.0 else 0 for nearest, pressure in zip(self._nearest, self._pressure)]}

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)

        self._pressure = self.np_random_integers(0, 10, size=4, dtype=np.int32)
        self._nearest = self.np_random_floats(0.5, 1.0, size=4, dtype=np.int32)
        for i in range(4):
            if self._pressure[i] == 0:
                self._nearest[i] = 1.0
        observation, info = self._get_obs(), self._get_info()
        return observation, info

    def step(self, action):
        pass
        observation, info = self._get_obs(), self._get_info()
        terminated = self._passed_cars >= 100
        truncated = False
        reward = -info.idle_cars
        return observation, reward, terminated, truncated,info
