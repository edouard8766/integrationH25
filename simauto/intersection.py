import os
from enum import Enum
from typing import Optional
import pygame
import numpy as np
import gymnasium as gym
from cars import DrivingCar

current_dir = os.path.dirname(os.path.abspath(__file__))

class TrafficLightState(Enum):
    SOUTH_NORTH_GREEN = 0
    SOUTH_NORTH_LEFT = 1
    NORTH_SOUTH_LEFT = 2
    WEST_EAST_GREEN = 3
    WEST_EAST_LEFT = 4
    EAST_WEST_LEFT = 5

    def to_array(self):
        array = np.zeros(6, dtype=np.int32)
        array[self.value] = 1
        return array


class IntersectionEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self._yellow_duration = 3.5
        self._lights_status = TrafficLightState.SOUTH_NORTH_GREEN
        self._frame_counter = 0 # counter pour clignotant

        self._passed_cars = 0
        self._pressure = np.array([0, 0, 0, 0], dtype=np.int32)  # Number of cars in each lane
        self._nearest = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)  # distance of nearest car from each lane

        self.observation_space = gym.spaces.Dict(
            {
                "pressure": gym.spaces.Box(low=0, high=50, shape=(4,), dtype=np.int32),
                "nearest": gym.spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32),
                "lights": gym.spaces.Box(low=0, high=1, shape=(6,), dtype=np.int32)
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

        # Create cars
        limite_vitesse = (50, 30)  # In km/h
        self.cars = [DrivingCar(200, 485, limite_vitesse[0], (1, 0))]  # Placeholder

        #position des lumieres
        self.traffic_light_positions = { #TOUS PLACEHOLDER, Il faut remplacer
            TrafficLightState.SOUTH_NORTH_GREEN: (0, 0),
            TrafficLightState.SOUTH_NORTH_LEFT: (0, 1),
            TrafficLightState.NORTH_SOUTH_LEFT: (0, 2),
            TrafficLightState.WEST_EAST_GREEN: (0, 3),
            TrafficLightState.WEST_EAST_LEFT: (0, 4),
            TrafficLightState.EAST_WEST_LEFT: (0, 5),
        }

    def _get_obs(self):
        return {"pressure": self._pressure,
                "nearest": self._nearest,
                "lights": self._lights_status.to_array(),}


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
        self._lights_status = TrafficLightState(action)

        # On peut pas savoir la lane des voitures (facilement (faire un enum Lane))
        #for car in self.cars:
        #    if car.lane in (Lane.WEST_EAST, Lane.EAST_WEST)
        #       and self._lights_status == TrafficLightState.WEST_EAST_GREEN:
        #            car.drive(go=True)
        #    if car.lane in (Lane.SOUTH_NORTH, Lane.NORTH_SOUTH)
        #       and self._lights_status == TrafficLightState.WEST_EAST_GREEN:
        #            car.drive(go=True)
        #    # Faire pour les lumières clignotantes également.

        self._passed_cars += np.random.randint(0,1)  # va falloir trouver quoi mettre pour les compter

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

        #render traffic lights et state
        for state, pos in self.traffic_light_positions.items():
            if state == self._lights_status:
                #si c'est un state prioritaire on clignoteeee
                if state in [TrafficLightState.SOUTH_NORTH_LEFT, TrafficLightState.WEST_EAST_LEFT, TrafficLightState.EAST_WEST_LEFT, TrafficLightState.NORTH_SOUTH_LEFT]:
                    #blink a chaque 15 frames?
                    if (self._frame_counter // 15) % 2 == 0:
                        img_path = os.path.join(current_dir, "items", "light_0.png")
                    else
                        img_path = os.path.join(current_dir, "items", "light_off.png")
                else:
                    img_path = os.path.join(current_dir, "items", "light_0.png") # verte normale
            else:
                #tous les autre sont rouges par principe
                img_path = os.path.join(current_dir, "items", "light_2.png")
            #load
            if os.path.exists(img_path):
                light_img = pygame.image.load(img_path)
            else:
                light_img = pygame.image.load(os.path.join(current_dir, "items", "light_2.png"))#si on trouve pas le default c'est red
            self.screen.blit(light_img, pos)
        pygame.display.update()
        self.clock.tick(30)#30 fps?
        self._frame_counter += 1


    # Dépendemment de comment on implémente l'agent
    # Pour l'instant, il choisi en temps réel,
    # donc il n'y a pas de cycle prédéfini
    #def _cycle_lights(self): # a implementer dans step
    #    #change and reset timers
    #    # va falloir mettre les bons cycle a chaque lumiere
    #    self._lights_status[:] = 0 #turn off all
    #    self._current_phase = (self._current_phase + 1) % len(self._lights_status) # cycle la light
    #    self._lights_status[self._current_phase] = 1 # turn on next green
    #    self._lights_timers[self._current_phase] = self._green_duration # reset timer


    def close(self):
        pygame.quit()
