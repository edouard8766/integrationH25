import os
from enum import Enum
from typing import Optional
import pygame
import math
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import random
from simauto.sim import *
from simauto.sim import IntersectionSimulation

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



        self.sim = IntersectionSimulation()
        self._action_space = spaces.Discrete(6)
        self._obs_space = gym.spaces.Dict({
            "pressure": gym.spaces.Box(low=0, high=1, shape=(8,), dtype=np.float32),
            "nearest": gym.spaces.Box(low=0, high=1, shape=(8,), dtype=np.float32),
            "lights": gym.spaces.Box(low=1, high=6, shape=(1,), dtype=np.float32),
        })

        self.steps_per_second = steps_per_second
        self.delta_time = 1.0/self.steps_per_second
        self.cars = []
        self.time = 0
        self.fps = 30
        self.truncated = False
        self.scale_factor = 10 #1m = 10 pixels
        self.wait_times = {}
        self._passed_cars = 0
        self.total_emissions = 0.0
        self.total_wait_time = 0.0
        self._pressure = np.array([0, 0, 0, 0], dtype=np.int32)  # Number of cars in each lane
        self._nearest = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)  # distance of nearest car from each lane

        self.intersection_lines = {
            0:  (433,503), #faire en sorte que la ligne soit juste une voie pour pas que les gens qui arrivent de l'autre bord arretent
            1:  (560,434),
            2:  (503,560),
            3:  (434,433)
        }

        pygame.init()
        self.screen = pygame.display.set_mode((1000, 1000))
        pygame.display.set_caption("Traffic Simulation")
        self.clock = pygame.time.Clock()

        # Load assets
        self.background = pygame.image.load(os.path.join(current_dir, "items", "Background.png"))
        self.background = pygame.transform.scale(self.background, (1000, 1000))


    def _get_obs(self):
        pressure = np.array(self._pressure)
        for car in self.sim.cars:
            if car.lane and car.lane.road.direction in [Direction.East, Direction.West]:
                pressure[0] += 1
            #le faire pour tous
        nearest = np.array(self._nearest)

        return {
            "pressure": pressure,
            "nearest": nearest,
            #"lights"
        }

    def _get_info(self):
        return {"idle_cars": [pressure if nearest == 0.0 else 0 for nearest, pressure in zip(self._nearest, self._pressure)]}

    def spawn_random_car(self, direction=None, intention=None):
        direction = direction or random.choice(list(Direction))
        intention = intention or random.choice(list(CarIntention))

        car = Car(
            speed = 5.0,# a verfier
            target_speed = 5.0, #a verifier
            intention = intention
        )
        self.sim.spawn_car(car,direction)
    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        self.sim = IntersectionSimulation()
        self.total_emissions = 0.0
        self.total_wait_time = 0.0
        # trouver avec les trucs de sim.py ->

        for _ in range(random.randint(5,15)):
            direction = random.choice(list(Direction))
            intention = (random.choice(list(CarIntention)))
            self.spawn_random_car(direction, intention)

        return self._get_obs()

    def _compute_reward(self):
        wait_time_list = []
        for car in self.sim.cars:
            wait_time = car.wait_time
            wait_time_list.append(wait_time)
        total_wait = sum(self.wait_times.values())
        mean_wait = total_wait / len(self.sim.cars) if self.sim.cars else 0.0
        variance = sum((x-mean_wait) ** 2 for x in wait_time_list) / (len(self.sim.cars)-1)
        ecart_type = math.sqrt(variance)

        if mean_wait <= 90:
            return max(0.0, 100 - mean_wait)  # diminue linéairement jusqu’à 0
        elif ecart_type > 2: #a verifier
            return -1e4
        else:
            return -math.exp((mean_wait - 90) / 10)  # pénalité exponentielle

    def _update_wait_time(self):
        for car in self.sim.cars:
            if car.speed < 0.1: #stopped
                self.wait_times[id(car)] = self.wait_times.get(id(car), 0) + self.delta_time
            else:
                self.wait_times[id(car)] = 0.0


    def step(self, action):
        self.sim.take_action(TrafficSignalPhase(action+1))# +1 car les phases commencent a 1

        #changer le state si necessaire ( jsp comment)
        self.sim.step(self.delta_time)
        self.time += 1 # si on fait 1 step par seconde

        self.total_emissions += self.sim.delta_emissions
        self._update_wait_time()

        observation, info = self._get_obs(), self._get_info()
        terminated = self._passed_cars >= 1000
        reward = self._compute_reward()
        return observation, reward, terminated, self.truncated, info


    def render(self, mode='human'):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.truncated = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.truncated = True


        self.screen.blit(self.background, (0, 0))



        pygame.display.update()

        self.clock.tick(self.fps)  # 30 fps?


    def close(self):
        pygame.quit()






