import os
from enum import Enum
from typing import Optional
import pygame
import numpy as np
import gymnasium as gym
from cars import DrivingCar
from trafficLight import TrafficLight

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
    def __init__(self, steps_per_second):
        super().__init__()
        self.steps_per_second = steps_per_second
        self._yellow_duration = 3.5
        self._yellow_counter = self._yellow_duration
        self.yellow_light_on = False
        self._lights_status = TrafficLightState.SOUTH_NORTH_GREEN.value # See class. Agent will output int between [0,5]
                                                                        # The corresponding light -> On, others -> off
        self.frame_counter = 0 # counter pour clignotant
        self.fps = 30
        self.truncated = False

        self._passed_cars = 0
        self._pressure = np.array([0, 0, 0, 0], dtype=np.int32)  # Number of cars in each lane
        self._nearest = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)  # distance of nearest car from each lane

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

        # Create cars
        limite_vitesse = (50, 30)  # In km/h
        self.cars = [DrivingCar(200, 485, limite_vitesse[0], (1, 0))]  # Placeholder
        self.traffic_lights = []
        for i in range(0,4):
            self.traffic_lights.append(TrafficLight(i, 2))

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
        if action != self._lights_status:
            self.set_yellow_lights(action)
        self._lights_status = action # Will be an int associated with a green light [0,5]. See Enum TrafficLightState

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
            # Je propose que ça se fasse dans cars. Quand l'auto franchi intersection, elle ajoute un à self._passed_cars

        self.frame_counter = 0 # reset counter

        observation, info = self._get_obs(), self._get_info()
        terminated = self._passed_cars >= 100
        reward = -np.sum(info["idle_cars"])
        return observation, reward, terminated, self.truncated, info


    def render(self, mode='human'):
        print("ok")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.truncated = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.truncated = True


        self.screen.blit(self.background, (0, 0))

        # Render traffic lights
        if self.yellow_light_on:
            self._yellow_counter -= 1
            if self._yellow_counter < 0:
                self.yellow_light_on = False
                self.set_lights_color()
                self.frame_counter = 0 # Reset to 0 so the agent can't take a decision right after the yellow light turns off
        else:
            self.set_lights_color()

        for light in self.traffic_lights:
            light.draw(self.screen)

        for car in self.cars:
            car.draw(self.screen)

        pygame.display.update()
        self.clock.tick(self.fps)  # 30 fps?
        self.frame_counter += 1


    def close(self):
        pygame.quit()


    def set_lights_color(self):
        if self._lights_status == TrafficLightState.SOUTH_NORTH_GREEN.value:
            self.traffic_lights[3].set_state(0) # south-north
            self.traffic_lights[2].set_state(0) # nort-south
            self.traffic_lights[1].set_state(2) # east-west
            self.traffic_lights[0].set_state(2) # west-east
        elif self._lights_status == TrafficLightState.SOUTH_NORTH_LEFT.value:
            self.traffic_lights[3].set_state(3)
            self.traffic_lights[2].set_state(2)
            self.traffic_lights[1].set_state(2)
            self.traffic_lights[0].set_state(2)
        elif self._lights_status == TrafficLightState.NORTH_SOUTH_LEFT.value:
            self.traffic_lights[3].set_state(2)
            self.traffic_lights[2].set_state(3)
            self.traffic_lights[1].set_state(2)
            self.traffic_lights[0].set_state(2)
        elif self._lights_status == TrafficLightState.WEST_EAST_GREEN.value:
            self.traffic_lights[3].set_state(2)
            self.traffic_lights[2].set_state(2)
            self.traffic_lights[1].set_state(0)
            self.traffic_lights[0].set_state(0)
        elif self._lights_status == TrafficLightState.WEST_EAST_LEFT.value:
            self.traffic_lights[3].set_state(2)
            self.traffic_lights[2].set_state(2)
            self.traffic_lights[1].set_state(2)
            self.traffic_lights[0].set_state(3)
        elif self._lights_status == TrafficLightState.EAST_WEST_LEFT.value:
            self.traffic_lights[3].set_state(2)
            self.traffic_lights[2].set_state(2)
            self.traffic_lights[1].set_state(3)
            self.traffic_lights[0].set_state(2)
        else:
            self.traffic_lights[3].set_state(2)
            self.traffic_lights[2].set_state(2)
            self.traffic_lights[1].set_state(2)
            self.traffic_lights[0].set_state(2)


    def set_yellow_lights(self, new_state):
        if new_state in (0, 3):
            if self._lights_status in (new_state+1, new_state+2): # if light_status goes from blinking_green to green in same axis
                return
        self.yellow_light_on = True
        self._yellow_counter = self._yellow_duration*self.fps
        if self._lights_status == TrafficLightState.SOUTH_NORTH_GREEN.value:
            if new_state == 1:
                self.traffic_lights[2].set_state(1)
            elif new_state == 2:
                self.traffic_lights[3].set_state(1)
            else:
                self.traffic_lights[2].set_state(1) # Set color to yellow
                self.traffic_lights[3].set_state(1)
        elif self._lights_status == TrafficLightState.SOUTH_NORTH_LEFT.value:
            self.traffic_lights[3].set_state(1)
        elif self._lights_status == TrafficLightState.NORTH_SOUTH_LEFT.value:
            self.traffic_lights[2].set_state(1)
        elif self._lights_status == TrafficLightState.WEST_EAST_GREEN.value:
            if new_state == 4:
                self.traffic_lights[1].set_state(1)
            elif new_state == 5:
                self.traffic_lights[0].set_state(1)
            else:
                self.traffic_lights[0].set_state(1)
                self.traffic_lights[1].set_state(1)
        elif self._lights_status == TrafficLightState.WEST_EAST_LEFT.value:
            self.traffic_lights[0].set_state(1)
        elif self._lights_status == TrafficLightState.EAST_WEST_LEFT.value:
            self.traffic_lights[1].set_state(1)


