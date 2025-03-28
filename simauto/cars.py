import pygame
import random
import math

class DrivingCar(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, direction, turn_choice):
        pygame.sprite.Sprite.__init__(self)
        filename = "items\\Car" + str(random.randint(0,0)) + ".png"
        self.image = pygame.image.load(filename)
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
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.x = x # (x,y) is the point at the front of the car, center between right and left
        self.rect.y = y
        #self.speed = random.randint(speed-5, speed+10)
        self.speed = speed
        self.turning = False # Set to True if car is turning
        self.driving = False # To check if cars in front is driving
        self.turn_choice = turn_choice # Defines in which direction car wants to turn ->
                                                     # 0:forward, 1:right, 2:left

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

    def drive(self):
        if self.driving and not self.turning:
            # Movement based on integer direction
            if self.direction == -1:  # Left
                self.rect.x += self.speed
            elif self.direction == 1:  # Right
                self.rect.x -= self.speed
            elif self.direction == 2:  # Down
                self.rect.y += self.speed
            elif self.direction == -2:  # Up
                self.rect.y -= self.speed
        if self.turning:
            pass
