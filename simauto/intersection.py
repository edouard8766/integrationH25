import os
import time
from typing import Optional
import pygame
import math
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import random
from simauto.sim import (
    IntersectionSimulation,
    CarIntention, Car, Lane,
    TrafficSignal, TrafficSignalPhase,
    Direction, Position, Viewport, Transform,
)
from typing import ClassVar

current_dir = os.path.dirname(os.path.abspath(__file__))

class Asset:
    ASSET_PATH: ClassVar[str] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

    @classmethod
    def load(cls, asset_name: str):
        return pygame.image.load(os.path.join(cls.ASSET_PATH, asset_name))

class Sprite:
    def __init__(self, surface):
        self.surface = surface

    def draw(self, screen, transform: Transform):
        rect = self.surface.get_rect(center=tuple(transform.position))
        surface = pygame.transform.rotate(self.surface, math.degrees(transform.rotation))
        screen.blit(surface, rect)


def draw_background(screen, background):
    screen.blit(background, (0,0))

def get_epsilon(episode, total_episodes, eps_start=0.99, eps_end=0.01, stable_ratio=0.1):
    decay_episodes = int(total_episodes * (1-stable_ratio))
    if episode >= decay_episodes:
        return eps_end
    decay_rate = np.log(eps_end/eps_start) / decay_episodes
    return eps_start * np.exp(decay_rate * episode)

def draw_traffic_light(screen, simulation, direction: Direction, from_opposite_side = False):
    screen_view = Viewport(screen.get_width(), screen.get_height())
    sim_view = IntersectionSimulation.VIEWPORT
    abs_view = Viewport(100, 100)
    approach_road = simulation.approach_road(direction)
    signal = simulation.signal_at(direction)
    first_lane = Lane(approach_road, 0)
    last_lane = Lane(approach_road, approach_road.lanes - 1)

    height_padding = Position(0).offset(direction.opposite, .4)
    width_padding = Position(0).offset(direction.left, 1.6).map(abs_view, sim_view)
    if from_opposite_side:
        offset = Position(0).offset(direction.opposite, 17).map(abs_view, sim_view)
    else:
        offset = Position(0).offset(direction.opposite, 4.8).map(abs_view, sim_view)

    start = (first_lane.end + offset - width_padding).map(sim_view, screen_view)
    end = (last_lane.end + offset + width_padding).map(sim_view, screen_view)

    height_padding = height_padding.map(abs_view, screen_view)
    points = tuple(start), tuple(start + height_padding), tuple(end + height_padding), tuple(end)

    color: pygame.Color
    blink_duration = .75
    blink = int(time.time() / blink_duration) % 2
    match signal:
        case TrafficSignal.Permitted | TrafficSignal.Protected:
            color = pygame.Color("green3")
        case TrafficSignal.Halt:
            color = pygame.Color("red3")

    if simulation.is_amber_at(direction):
        color = pygame.Color("yellow")

    
    if signal is TrafficSignal.Protected and blink:
        return
    
    pygame.draw.polygon(screen, color, points)
        

class IntersectionEnv(gym.Env):
    def __init__(self, step_length, render_mode=None):
        self.step_length = step_length
        self.sim = IntersectionSimulation()
        self.render_mode = render_mode

        self.mean_waits = []

        self.episode_end_threshold = 100 # in numbers of cars passed

        self.action_space = spaces.Discrete(6)
        self.observation_space = gym.spaces.Dict({
            # Number of cars in each approach road
            "pressure": gym.spaces.Box(low=0, high=np.inf, shape=(4,), dtype=np.int64),

            # Distance of the nearest car in each approach road
            "nearest": gym.spaces.Box(low=-np.inf, high=max(
                self.sim.VIEWPORT.width, self.sim.VIEWPORT.height
            ), shape=(4,), dtype=np.float64),

            #  Current traffic light phase
            #"lights": gym.spaces.Box(low=0, high=1, shape=(6,), dtype=np.int64),
        })

        self.metadata = {
            "render_modes": ["human"],
            "render_fps": 30,
        }

        if self.render_mode == "human":
            pygame.init()
            self._render_viewport = Viewport(500, 500)
            self._render_screen = pygame.display.set_mode(
                (self._render_viewport.width, self._render_viewport.height)
            )
            pygame.display.set_caption("Traffic Simulation")
            self._render_clock = pygame.time.Clock()
            self._render_background = pygame.transform.scale(
                Asset.load("Background.png"),
                (self._render_viewport.width, self._render_viewport.height)
            )
            car_image = Asset.load("car0.png")
            car_image = pygame.transform.rotate(car_image, -90)
            car_image = pygame.transform.scale(
                car_image,
                (self._render_viewport.width/20, self._render_viewport.height/20)
            )
            self._render_car = Sprite(car_image)

        self.elapsed_time = 0
        self.truncated = False
        self._passed_cars = 0
        self._pressure = np.array([0, 0, 0, 0], dtype=np.int32)  # Number of cars in each lane
        self._nearest = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)  # Distance of nearest car from each lane

    def _get_obs(self):
        pressure = np.array([0, 0, 0, 0], dtype=np.int64)
        nearest = np.array([self.sim.approach_road(direction).length + 10 for direction in list(Direction)], dtype=np.float64)
        #lights = np.array([1 if i == self.sim.phase.value else 0 for i in range(6)], dtype=np.int64)

        for car in self.sim.cars:
            if car.road is None:
                continue  # Skip cars that are mid-transition

            approach = car.road.direction.opposite
            approach_road = self.sim.approach_road(approach)
            if car.road is approach_road:
                distance = approach_road.length - car.distance
                pressure[approach.value] += 1
                if nearest[approach.value] < distance:
                    nearest[approach.value] = distance

        return {
            "pressure": pressure,
            "nearest": nearest,
            #"lights" : lights,
        }

    def _get_info(self):
        return { "total_emissions": self.sim.emissions, "elapsed_time": self.elapsed_time }

    def spawn_random_car(self, direction=None, intention=None):
        if len(self.sim.cars) >= 40:  # Max 40 cars
            return
        direction = direction or random.choice(list(Direction))
        intention = intention or random.choice(list(CarIntention))

        # Vitesses à verifier (peut-être les changer pour chaque rues)
        car = Car(
            speed = 10,
            target_speed = 10,
            intention = intention
        )
        self.sim.spawn_car(car, direction)

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        self.sim.reset(phase=random.choice(list(TrafficSignalPhase)))
        self.elapsed_time = 0
        self.truncated = False
        self._passed_cars = 0
        self.mean_waits = []

        # trouver avec les trucs de sim.py ->

        for _ in range(random.randint(5,15)):
            self.spawn_random_car()

        observation, info = self._get_obs(), self._get_info()

        return observation, info

        '''
    def _compute_reward(self):
        if not self.sim.cars:
            return 0.

        wait_times = [car.wait_time for car in self.sim.cars]
        total_wait = sum(wait_times)
        mean_wait = total_wait / len(self.sim.cars)

        if len(self.sim.cars) > 1:
            variance = sum((wait - mean_wait) ** 2 for wait in wait_times) / (len(self.sim.cars) - 1)
            std_dev = math.sqrt(variance)
        else:
            variance = 0.
            std_dev = 0.

        if mean_wait <= 90.:
            reward = max(0., 100. - mean_wait)  # diminue linéairement jusqu’à 0
        else:
            penalty = ((mean_wait-90)/10) **2 #exponentielle
            reward = 10 - penalty

        if std_dev > 15:
            reward -= min(50., std_dev)
        cars_passed = len(self.sim.cars)
        reward += cars_passed * 1.5
        max_wait = max(wait_times)

        #penalise pour emission
        emission_penalty = self.sim.emissions * 0.001
        reward -= emission_penalty
        if max_wait > 300.:
            reward -= (max_wait - 300.) * 0.1

        self.mean_waits.append(mean_wait)

        return reward
        '''

    def _compute_reward(self):
        if not self.sim.cars:
            return 0.0

        wait_times = [car.wait_time for car in self.sim.cars]
        total_wait = sum(wait_times)

        wait_penalty = -0.015 * total_wait

        std_dev = np.std(wait_times) if len(wait_times) > 1 else 0.0
        fairness_penalty = -0.15 * std_dev
        car_count_penalty = -0.35 * np.log(len(self.sim.cars)+1)


        max_wait = max(wait_times) if wait_times else 0.0
        emergency_penalty = -0.6 * max(0.0, max_wait - 300.0) #**2 #si ca marche encore pas

        reward = (
            wait_penalty
            + fairness_penalty
            + emergency_penalty
            + car_count_penalty
        )

        self.mean_waits.append(total_wait/len(wait_times))

        return reward

    def step(self, action):
        assert self.action_space.contains(
                action
        ), f"{action!r} ({type(action)}) invalid"

        new_phase = TrafficSignalPhase(action)
        self.sim.phase = new_phase

        # Spawn new cars
        if self._passed_cars < self.episode_end_threshold and random.random() < 0.10:  # 10% chance per step to spawn a group of cars
            common_direction = random.choice(list(Direction))
            for _ in range(0, random.randint(4, 8)):
                if random.randint(0,10) < 8:
                    direction = common_direction
                else:
                    direction = random.choice(list(Direction))
                self.spawn_random_car(direction=direction)

        previous_car_count = len(self.sim.cars)

        if self.step_length < 0.03:
            self.sim.step(self.step_length)
        else:
            substeps = math.ceil(self.step_length / 0.03)
            substep_length = self.step_length / substeps
            for _ in range(substeps):
                self.sim.step(substep_length)

        self.elapsed_time += self.step_length
        passed_cars = previous_car_count - len(self.sim.cars)
        self._passed_cars += passed_cars

        observation, info = self._get_obs(), self._get_info()
        terminated = self._passed_cars >= self.episode_end_threshold
        reward = self._compute_reward()

        return observation, reward, terminated, self.truncated, info

    def render(self):
        if self.render_mode != "human":
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.truncated = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.truncated = True
        
        draw_background(self._render_screen, self._render_background)
        
        for direction in list(Direction):
            draw_traffic_light(self._render_screen, self.sim, direction)

        for car in self.sim.cars:
            self._render_car.draw(self._render_screen, car.transform.map(
                self.sim.VIEWPORT, self._render_viewport)
            )

        pygame.display.update()

        self._render_clock.tick(self.metadata["render_fps"])

    def close(self):
        pygame.quit()

