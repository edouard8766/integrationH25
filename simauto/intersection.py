import os
from enum import Enum
from typing import Optional
import pygame
import numpy as np
import gymnasium as gym
import random

current_dir = os.path.dirname(os.path.abspath(__file__))






LANE_START_POSITIONS = {
    1: (605, 485),
    2: (605, 453),
    3: (485, 395),
    4: (452, 395),
    5: (395, 515),
    6: (395, 547),
    7: (516, 565),
    8: (548, 565)
}
LANE_TURN_POSITIONS = {
    1: (516, 565),
    2: (605, 517),
    3: (549, 395),
    4: (517, 395),
    5: (395, 515),
    6: (395, 547),
    7: (516, 565),
    8: (548, 565)
}


class IntersectionEnv(gym.Env):
    def __init__(self, steps_per_second):
        super().__init__()




        self.steps_per_second = steps_per_second
        self._yellow_duration = 3.5
        self._yellow_counter = self._yellow_duration
        self.yellow_light_on = False

        self.frame_counter = 0 # counter pour clignotant
        self.fps = 30
        self.truncated = False

        self._passed_cars = 0
        self._pressure = np.array([0, 0, 0, 0], dtype=np.int32)  # Number of cars in each lane
        self._nearest = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)  # distance of nearest car from each lane

        self.intersection_lines = {
            0:  (433,503), #faire en sorte que la ligne soit juste une voie pour pas que les gens qui arrivent de l'autre bord arretent
            1:  (560,434),
            2:  (503,560),
            3:  (434,433)
        }
        self.observation_space = gym.spaces.Dict(
            {
                "pressure": gym.spaces.Box(low=0, high=50, shape=(4,), dtype=np.int32),
                "nearest": gym.spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32),
                "lights": gym.spaces.Box(low=0, high=1, shape=(1,), dtype=np.int32)
            }
        )
        self.action_space = gym.spaces.Discrete(6)

        pygame.init()
        self.screen = pygame.display.set_mode((1000, 1000))
        pygame.display.set_caption("Traffic Simulation")
        self.clock = pygame.time.Clock()

        # Load assets
        self.background = pygame.image.load(os.path.join(current_dir, "items", "Background.png"))
        self.background = pygame.transform.scale(self.background, (1000, 1000))


    def _get_obs(self):
        return {"pressure": self._pressure,
                "nearest": self._nearest,
                "lights": self._lights_status}


    def _get_info(self):
        return {"idle_cars": [pressure if nearest == 0.0 else 0 for nearest, pressure in zip(self._nearest, self._pressure)]}


    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)

        self._pressure = self.np_random.integers(0, 10, size=4, dtype=np.int32)
        self._nearest = self.np_random.uniform(0.5, 1.0, size=4).astype(np.float32)
        self._passed_cars = 0
        for i in range(4):
            if self._pressure[i] == 0:
                self._nearest[i] = 1.0
        observation, info = self._get_obs(), self._get_info()
        return observation, info


    def step(self, action):


        observation, info = self._get_obs(), self._get_info()
        terminated = self._passed_cars >= 100
        reward = -np.sum(info["idle_cars"])
        return observation, reward, terminated, self.truncated, info


    def render(self, mode='human'):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.truncated = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.truncated = True


        self.screen.blit(self.background, (0, 0))

        delta_time = self.clock.tick(60) / 10

        pygame.display.update()
        self.clock.tick(self.fps)  # 30 fps?
        self.frame_counter += 1


    def close(self):
        pygame.quit()






