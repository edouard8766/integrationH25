import math
import random
import pygame
import cars

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
class Background(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("items\\Background.png")
        self.image = pygame.transform.scale(self.image, (1000,1000))

    def draw(self):
        screen.blit(self.image, (0,0))

turn_choice = 1
background = Background()
car = cars.DrivingCar(200, 485, 2, (1,0), turn_choice)
'''
Possible starting pos:
dir[1,0] -> (0,452), (0,485)
dir[-1,0] -> (screenWidth+car_length,452), (screeWidth+car_length,485)
dir[0,1] -> (452,0), (485,0)
dir[0,-1] -> (452,screenHeight+car_length), (485,screeHeight+car_length)
'''
for i in range(1, 9):
    globals()[f'Lane_{i}'] = []

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

#Transform direction and turn choice to lane number
def get_lane_number(direction, turn_choice):
    # Define the base lane based on direction
    if direction == -1:  # Left
        lane_number = 5  # Lane 5 is at 180 degrees (facing left)
    elif direction == 0:  # Straight (forward)
        lane_number = 1  # Lane 1 is at 0 degrees (facing right)
    elif direction == 1:  # Right
        lane_number = 3  # Lane 3 is at 90 degrees (facing up)
    elif direction == 2:  # Reverse (not used in this case)
        lane_number = 7  # Lane 7 is at 270 degrees (facing down)
    else:
        print("Invalid direction")

    if turn_choice > 0:
        lane_number += 1
    elif turn_choice < 0:
        pass
    else:
        print("invalid turn_choice")
        print(turn_choice)
    return lane_number

#Create cars and place them in the lanes
num_cars = 10
for i in range(num_cars):
    direction = random.randint(-1, 2)
    speed = random.uniform(2, 3)
    turn_choice = 0
    while turn_choice == 0:
        turn_choice = random.randint(-3,3) # Defines in which direction car wants to turn ->
                                            #negative = left, positive = right
                                            # 1-2:forward, 3:turn

    x = 100 #not set yet
    y = 100
    car = cars.DrivingCar(x, y, speed, direction, turn_choice)
    lane = get_lane_number(direction, turn_choice)
    lanes[lane].append(car)




while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                drive = True
            elif event.key == pygame.K_ESCAPE:
                run = False

    background.draw()
    car.drive(drive)
    car.draw(screen)
    pygame.display.update()

    Clock.tick(fps)
pygame.quit()
