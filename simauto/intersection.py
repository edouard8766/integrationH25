import os
from typing import Optional
import pygame
import numpy as np
import gymnasium as gym
from cars import DrivingCar

current_dir = os.path.dirname(os.path.abspath(__file__))

class IntersectionEnv(gym.Env):
    def __init__(self):
        super().__init__()
        #duree des lights pour les steps
        self._yellow_duration = 3.5
        self._green_duration = 15
        self._red_duration = 15
        self._lights_timers = np.zeros(6, dtype=np.float32) # timer pour chaque lum
        self._lights_status = np.array([0, 0, 0, 0, 0, 0], dtype=np.int32) #jla comprends bof mais merci
        self._current_phase = 0 # pour savoir laquelle est VERTE

        self._passed_cars = 0
        self._pressure = np.array([0, 0, 0, 0], dtype=np.int32) # nb of cars in each lane
        self._nearest = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32) # distance of nearest car from each lane
        # [0]: greenH, [1]: leftTurnH1, [2]: leftTurnH1, [3]: greenV, [4]: leftTurnV1, [5]: leftTurnV2

        self.observation_space = gym.spaces.Dict(
            {
                "pressure": gym.spaces.Box(low=0, high=50, shape=(4,), dtype=np.int32),
                "nearest": gym.spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32),
                "lights": gym.spaces.Box(low=0, high=1, shape=(6,), dtype=np.int32)
            }
        )
        self.action_space = gym.spaces.Discrete(6)  # dim. = 6 because light_status has 6 lights to control
        #pygame init
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 1000))
        pygame.display.set_caption("Traffic Simulation")
        self.clock = pygame.time.Clock()

        # Load assets
        self.background = pygame.image.load(os.path.join(current_dir, "items", "Background.png"))
        self.background = pygame.transform.scale(self.background, (1000, 1000))

        # Create cars
        limite_vitesse = 50 #va falloir ajuster le 50 km/h pour des pixels/seconde
        self.cars = [DrivingCar(200, 485, limite_vitesse, (1, 0))]#une seule, faut automatiser


    def _get_obs(self):
        return {"pressure": self._pressure,
                "nearest": self._nearest,
                "lights": self._lights_status,}


    def _get_info(self):
        return {"idle_cars": [pressure if nearest == 0.0 else 0 for nearest, pressure in zip(self._nearest, self._pressure)]}


    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)

        self._pressure = self.np_random.integers(0, 10, size=4, dtype=np.int32)
        self._nearest = self.np_random.uniform(0.5, 1.0, size=4).astype(np.float32)
        self._passed_cars = 0 #on le remet a 0?
        for i in range(4):
            if self._pressure[i] == 0:
                self._nearest[i] = 1.0
        observation, info = self._get_obs(), self._get_info()
        return observation, info


    def step(self, action):
        #ajouter les lumieres a hugo
        self._lights_status[action] = 1 - self._lights_status[action] #toggle on off, faut mettre JAUNE
        #sim car movement si vert
        for car in self.cars:
            if self._lights_status[0] == 1:
                car.drive(go=True)

        self._passed_cars += np.random.randint(0,1)# va falloir trouver quoi mettre pour les compter

        observation, info = self._get_obs(), self._get_info()
        terminated = self._passed_cars >= 100
        truncated = False
        reward = -np.sum(info["idle_cars"])
        return observation, reward, terminated, truncated, info


    def render(self, mode='human'):
        #on utilise pygame pour le display seulement maisssss
        self.screen.blit(self.background, (0, 0))

        for car in self.cars:
            car.draw(self.screen)

        for i, light_state in enumerate(self._lights_status):
            # les fichier sont nomme avec les couleurs faut changer pour chiffre
            light_image = pygame.image.load(os.path.join(current_dir, "items", "Lights", f"light_{light_state}.png")) 
            #light_pos = []
            #light_x transforme pour orientation peut-etre?
            #self.screen.blit(light_image, light_pos)

        pygame.display.update()
        self.clock.tick(30)#30 fps?


    def _change_lights(self): # a implementer dans step
        #change and reset timers
        # va falloir mettre les bons cycle a chaque lumiere
        self._lights_status[:] = 0 #turn off all
        self._current_phase = (self._current_phase + 1) % len(self._lights_status) # cycle la light
        self._lights_status[self._current_phase] = 1 # turn on next green
        self._lights_timers[self._current_phase] = self._green_duration # reset timer


    def close(self):
        pygame.quit()
