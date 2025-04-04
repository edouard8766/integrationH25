import math
import random
import pygame
import cars
import copy
import time

start_time = time.time()

pygame.init()
fps = 30
Clock = pygame.time.Clock()
screenWidth = 1000
screenHeight = 1000
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Simulation Auto")
icon = pygame.image.load("items\\Icon.png")
pygame.display.set_icon(icon)

pygame.mixer.music.load("items\\Music.mp3")
pygame.mixer.music.play(-1)

run = True
drive = False
MIN_DISTANCE = 60 # pixels

class Background(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("items\\Background.png")
        self.image = pygame.transform.scale(self.image, (1000,1000))

    def draw(self):
        screen.blit(self.image, (0,0))

turn_choice = 1
background = Background()

for i in range(1, 9):
    globals()[f'Lane_{i}'] = []

moving_cars = []

# Create a dictionary for lane numbers to lists
lanes = {
    1: Lane_1,
    2: Lane_2,
    3: Lane_3,
    4: Lane_4,
    5: Lane_5,
    6: Lane_6,
    7: Lane_7,
    8: Lane_8,
}
# Create car with proper position and direction tuple
direction_map = {
    -1: (-1, 0),  # Left
    0: (1, 0),  # Right
    1: (0, 1),  # Down
    2: (0, -1)  # Up
}
LANE_START_POSITIONS = {
    1: [(605, 485)],
    2: [(605, 453)],
    3: [(485, 395)],
    4: [(452, 395)],
    5: [(395, 515)],
    6: [(395, 547)],
    7: [(516, 565)],
    8: [(548, 565)]
}
LANE_TURN_POSITIONS = {
    1: [(605, 485)],
    2: [(605, 453)],
    3: [(485, 395)],
    4: [(452, 395)],
    5: [(395, 515)],
    6: [(395, 547)],
    7: [(516, 565)],
    8: [(548, 565)]
}
L1 = 140.16
L2 = 61.94
#Transform direction and turn choice to lane number
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


def make_cars_move(lanes):
    """Enable cars to drive based on distance of car ahead"""
    for lane_num in lanes:
        lane = lanes[lane_num]
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
                if prev_car.driving and distance > MIN_DISTANCE:
                    car.driving = True
                    print("now drive")


#Create cars and place them in the lanes

num_cars = 1
for i in range(num_cars):
    direction = random.choice([-2, -1, 1, 2])
    speed = random.uniform(2, 2.5)
    turn_choice = -3
    y = 0
    x = 0
    car_spacing = random.randint(50, 60)
    #while turn_choice == 0:
        #turn_choice = random.randint(-3,3) # Defines in which direction car wants to turn ->
                                            #negative = left, positive = right
                                            # 1-2:forward, 3:turn



    lane = get_lane_number(direction, turn_choice)
    base_pos = random.choice(LANE_START_POSITIONS[lane])

    # Calculate position based on existing cars in lane
    existing_cars = len(lanes[lane])
    x, y = base_pos

    # Adjust position based on direction and car count
    if direction in (1, -1):  # Horizontal movement
        offset = existing_cars * car_spacing
        x = x + offset if direction == 1 else x - offset
    else:  # Vertical movement
        offset = existing_cars * car_spacing
        y = y - offset if direction == 2 else y + offset
    car = cars.DrivingCar(x, y, speed, direction, turn_choice, lane)
    lanes[lane].append(car)

# (Pour Simon&LC) RectTopleft(0,1317) --- RectBotRight(1317,1682) --- CarreTopRight(1682,1317) Divise 3


while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                drive = True
            elif event.key == pygame.K_ESCAPE:
                run = False
    delta_time = Clock.tick(60) / 10
    background.draw()
    car.drive(delta_time)
    car.draw(screen)
    # Update and draw all cars in all lanes
    if drive:
        make_cars_move(lanes)  # Handle car movement logic

    # Draw all cars in all lanes
    for lane_num in lanes:
        for car in lanes[lane_num]:
            car.drive(delta_time)  # Update car position
            car.draw(screen)  # Draw the car
    pygame.display.update()

    Clock.tick(fps)
pygame.quit()
