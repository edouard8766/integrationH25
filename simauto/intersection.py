import os
from enum import Enum
from typing import Optional
import pygame
import numpy as np
import gymnasium as gym
from simauto.car import Car
from trafficLight import TrafficLight
from cars import DrivingCar
import random

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

def get_lane_number(direction, turn_choice):
    # Define the base lane based on direction
    if direction == -1:  # Left
        lane_number = 5  # Lane 5 is at 180 degrees (facing left)
    elif direction == -2:  # Straight (forward)
        lane_number = 7  # Lane 1 is at 0 degrees (facing right)
    elif direction == 1:  # Right
        lane_number = 1  # Lane 3 is at 90 degrees (facing up)
    elif direction == 2:  # Reverse (not used in this case)
        lane_number = 3  # Lane 7 is at 270 degrees (facing down)
    else:
        print("Invalid direction")

    if turn_choice > 0:
        lane_number += 1
    elif turn_choice < 0:
        pass
    else:
        lane_number = 0
        print("invalid turn_choice")
        print(turn_choice)
    return lane_number




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

        for i in range(1, 9):
            globals()[f'Lane_{i}'] = []

        self.moving_cars = []
        self.MIN_DISTANCE = 60  # pixels

        # Create a dictionary for lane numbers to lists
        self.lanes = {
            1: Lane_1,
            2: Lane_2,
            3: Lane_3,
            4: Lane_4,
            5: Lane_5,
            6: Lane_6,
            7: Lane_7,
            8: Lane_8,
        }



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

        num_cars = 1
        for i in range(num_cars):
            direction = random.choice([-2, -1, 1, 2])
            speed = random.uniform(2, 2.5)
            turn_choice = 0
            y = 0
            x = 0
            car_spacing = random.randint(50, 60)
            while turn_choice == 0:
                turn_choice = random.randint(-3,3) # Defines in which direction car wants to turn ->
            # negative = left, positive = right
            # 1-2:forward, 3:turn

            lane = get_lane_number(direction, turn_choice)
            base_pos = LANE_START_POSITIONS[lane]

            # Calculate position based on existing cars in lane
            existing_cars = len(self.lanes[lane])
            x, y = base_pos

            # Adjust position based on direction and car count
            if direction in (1, -1):  # Horizontal movement
                offset = existing_cars * car_spacing
                x = x + offset if direction == 1 else x - offset
            else:  # Vertical movement
                offset = existing_cars * car_spacing
                y = y - offset if direction == 2 else y + offset
            car = DrivingCar(x, y, speed, direction, turn_choice, lane)
            self.lanes[lane].append(car)



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

        delta_time = self.clock.tick(60) / 10
        self.make_cars_move()  # Handle car movement logic
        for lane_num in self.lanes:
            for car in self.lanes[lane_num]:
                car.drive(delta_time)  # Update car position
                car.draw(self.screen)  # Draw the car

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

    def check_intersection_cross(self, car: Car) -> bool:
        if car.direction in self.intersection_lines:
            crossing_line = self.intersection_lines[car.direction]
            if car.speed > 0 :#and not car.crossed_line:
                car.crossed_line = True
                return True
        return False

    def make_cars_move(self):
        """Enable cars to drive based on distance of car ahead"""
        for lane_num in self.lanes:
            lane = self.lanes[lane_num]
            for i, car in enumerate(lane):
                if i == 0:  # First car in lane
                    # Let first car drive if not already
                    if not car.driving:
                        car.driving = True
                        if not car.turning:
                            car.turning = True
                        print("car set to drive")
                else:
                    # Get previous car in lane
                    prev_car = lane[i - 1]

                    # Calculate distance based on direction
                    if abs(car.direction) == 1:  # Horizontal movement
                        distance = abs(prev_car.rect.x - car.rect.x)
                    else:  # Vertical movement
                        distance = abs(prev_car.rect.y - car.rect.y)

                    # Enable driving if previous car is moving and distance is sufficient
                    if prev_car.driving and distance > self.MIN_DISTANCE:
                        car.driving = True
                        print("now drive")



