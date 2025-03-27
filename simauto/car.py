from enum import Enum
from typing import Optional


class CarIntention(Enum):
    CONTINUE = "Continue"
    TURN_LEFT = "TurnLeft"
    TURN_RIGHT = "TurnRight"


class Car:
    def __init__(self, target_speed: float, speed: float, direction: int, intention: CarIntention,
                 acceleration: float = 7.2, deceleration: float = 10.8, turn_speed_factor: float = 0.5):
        """
target_speed: (km/h).
speed: Initial speed (km/h).
acceleration: (km/h2).
deceleration: (km/h2).
turn_speed_factor:  50% speed
        """
        self.target_speed = target_speed
        self.speed = speed
        self.direction = direction # 0:vers Nord, 1 vers est, 2 vers sud, 3 vers ouest
        self.intention = intention
        self.acceleration = acceleration
        self.deceleration = deceleration
        self.turn_speed_factor = turn_speed_factor


        self.crossed_intersection = False  # True quand on traverse la ligne, fait enclencher la turn animation
        self.turning = False  # True quand animation TURN_XY joue

    def step(self, stop_distance: Optional[float], delta_time: float, crossed_line: bool) -> float:

        if not self.crossed_intersection and crossed_line:
            self.crossed_intersection = True  #bravo tu as traverse
            if self.intention in {CarIntention.TURN_LEFT, CarIntention.TURN_RIGHT}:
                self.turning = True  # Start animation

        if self.turning:
            self.speed = self.target_speed * self.turn_speed_factor

        elif stop_distance is None:
            # Accelerate smoothly up to target speed
            if self.speed < self.target_speed:
                self.speed = min(self.target_speed, self.speed + self.acceleration * delta_time)
        else:
            # Calculate stopping distance based on current speed and deceleration
            required_stop_distance = (self.speed / 3.6 ** 2) / (2 * self.deceleration / 3.6)
            if stop_distance < required_stop_distance:
                self.speed = max(0, self.speed - self.deceleration * (delta_time / 3600))

        return self.speed * delta_time  # Distance traveled