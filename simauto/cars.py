import pygame
import random
import math


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
    1: (505, 558),
    2: (642, 443),
    3: (557, 495),
    4: (440, 357),
    5: (497, 444),
    6: (357, 560),
    7: (445, 465),
    8: (558, 603)
}


class DrivingCar(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, direction, turn_choice, lane):
        pygame.sprite.Sprite.__init__(self)
        filename = "items\\Car" + str(random.randint(0,0)) + ".png"
        self.image = pygame.image.load(filename)
        self.lane = lane
        self.side_length = 50
        self.front_buffer = 5 # The current car image has a few empty pixels at the front of the car
        self.image = pygame.transform.scale(self.image, (self.side_length,self.side_length))
        self.direction = direction
        # Set initial rotation based on direction
        if direction == 1:  # Right
            angle = 90
        elif direction == -1:  # Left
            angle = 270
        elif direction == 2:  # Down
            angle = 180
        elif direction == -2:  # Up
            angle = 0
        self.original_image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.x = x # (x,y) is the point at the front of the car, center between right and left
        self.rect.y = y
        #self.speed = random.randint(speed-5, speed+10)
        self.speed = speed
        self.turning = False # Set to True if car is turning
        self.driving = False # To check if cars in front is driving
        self.turn_choice = turn_choice # Defines in which direction car wants to turn ->

        self.turn_end = (0, 0)
        self.turn_start = (0, 0)
        self.turn_time = 0
        # Store original image for rotation
        self.image = self.original_image.copy()
        self.base_angle = 0  # Store initial rotation

        # Add turn completion flag
        self.turn_complete = False

    def update_car_state(self, a: tuple, b: tuple, T: float, v: float, lane: int) -> tuple:
        """
        Computes the new position and angle of the car image.

        Parameters:
            a (tuple): Starting point (x, y)
            b (tuple): Reference point (x, y) for curved trajectories
            T (float): Elapsed time
            v (float): Speed of the car
            lane (int): Lane number (odd for left turns, even for right turns)
                          - Uses L = 140.16 if lane is odd (left turn)
                          - Uses L = 61.95 if lane is even (right turn)

        Returns:
            tuple: (new_position, new_angle)
                - new_position: tuple representing the new (x, y) position
                - new_angle: float representing the new angle in radians
        """
        # Compute differences from the provided points.
        h = b[1] - a[1]
        s = a[0] - b[0]
        # Set L depending on the turning direction.
        L = 140.16 if lane % 2 == 1 else 61.95

        # Compute the trajectory distance using modulo to loop within L.
        d = min(v * T, L)

        def g(t: float) -> float:
            """
            Compute the inclination angle based on the time/distance along the curve.
            Formula: arctan(-|h| cos(πt/(2L)) / (|s| sin(πt/(2L)))
            """
            if L <= 0:
                raise ValueError("L must be positive and non-zero")
            numerator = -abs(h) * math.cos(math.pi * t / (2 * L))
            denominator = abs(s) * math.sin(math.pi * t / (2 * L))
            if denominator == 0:
                return math.copysign(math.pi / 2, numerator)
            return math.atan(numerator / denominator)

        def f(t: float) -> tuple:
            """
            Compute the position along the trajectory based on the time/distance parameter.

            Cases:
              1. Pure vertical movement if s == 0.
              2. Pure horizontal movement if h == 0.
              3. Curved trajectory otherwise.
            """
            a_x, a_y = a
            b_x, b_y = b

            if s == 0 and h == 0:
                raise ValueError("s and h cannot both be zero")

            # Case 1: Vertical movement.
            if s == 0:
                direction = 1 if h > 0 else -1
                return (a_x, a_y + direction * t)

            # Case 2: Horizontal movement.
            if h == 0:
                direction = 1 if s > 0 else -1
                return (a_x - direction * t, a_y)

            if lane == 3 or lane == 7:
                angle = math.pi * t / (2 * L)
                return (
                    s * math.cos(angle) + b_x,
                    h * math.sin(angle) + a_y
                )
            elif lane == 1 or lane == 5:
                angle = math.pi * t / (2 * L)
                return (
                    -s * math.sin(angle) + a_x,
                    -h * math.cos(angle) + b_y
                )
            else:
                #Handle rest
                angle = math.pi * t / (2 * L)
                return (
                    -s * math.sin(angle) + a_x,
                    -h * math.cos(angle) + b_y
                )

        new_position = f(d)
        new_angle = g(d)
        return new_position, new_angle

    def draw(self, screen):
        if self.direction == 1:
            x = self.rect.x - self.side_length + self.front_buffer
            y = self.rect.y - self.side_length/2
        elif self.direction == -1:
            x = self.rect.x - self.front_buffer
            y = self.rect.y - self.side_length / 2
        elif self.direction == 1:
            y = self.rect.y - self.side_length + self.front_buffer
            x = self.rect.x - self.side_length / 2
        else:
            y = self.rect.y - self.front_buffer
            x = self.rect.x - self.side_length / 2
        screen.blit(self.image, (x, y))

    def drive(self, delta_time):
        if self.driving and not self.turning:
            # Movement based on integer direction
            if self.direction == 1:  # Right
                self.rect.x += self.speed
            elif self.direction == -1:  # Left
                self.rect.x -= self.speed
            elif self.direction == 2:  # Down
                self.rect.y += self.speed
            elif self.direction == -2:  # Up
                self.rect.y -= self.speed


        if self.turning and not self.turn_complete:
            self.turn_start = LANE_START_POSITIONS[self.lane]
            self.turn_end = LANE_TURN_POSITIONS[self.lane]

            # Use actual delta_time for smooth animation
            self.turn_time += delta_time

            # Calculate progress (0-1) through the turn
            L = 140.16 if self.lane % 2 == 1 else 61.95
            progress = min(self.turn_time * self.speed / L, 1.0)

            # Get position and angle
            pos, angle = self.update_car_state(
                self.turn_start,
                self.turn_end,
                self.turn_time,
                self.speed,
                self.lane
            )

            # Update position and rotation
            self.rect.x, self.rect.y = pos
            rot = 90 if self.lane % 2 == 1 else -90
            self.image = pygame.transform.rotate(self.original_image, math.degrees(angle) + self.base_angle + rot)

            # Check if turn completed
            if progress >= 1.0:
                self.turn_complete = True
                self.turning = False
                self.driving = True
                print(self.direction)
                print(self.turn_choice)
                if self.direction == -1 and self.turn_choice > 0:
                    self.direction = -2
                elif self.direction == -1 and self.turn_choice > 0:
                    self.direction = 2
                elif self.direction == 1 and self.turn_choice > 0:
                    self.direction = 2
                elif self.direction == 1 and self.turn_choice < 0:
                    self.direction = -2
                elif self.direction == 2 and self.turn_choice > 0:
                    self.direction = -1
                elif self.direction == 2 and self.turn_choice < 0:
                    self.direction = 1
                elif self.direction == -2 and self.turn_choice > 0:
                    self.direction = 1
                elif self.direction == -2 and self.turn_choice < 0:
                    self.direction = -1
                print(self.direction)


