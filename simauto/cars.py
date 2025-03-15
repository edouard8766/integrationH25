import pygame
import random
import math
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

class DrivingCar(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, direction):
        pygame.sprite.Sprite.__init__(self)
        filename = os.path.join(current_dir, "items", "Car" + str(random.randint(0,0)) + ".png")

        self.image = pygame.image.load(filename)
        self.side_length = 50
        self.front_buffer = 5 # The current car image has a few empty pixels at the front of the car
        self.image = pygame.transform.scale(self.image, (self.side_length,self.side_length))
        self.direction = direction
        if direction[0] == 1:
            angle = 270
        elif direction[0] == -1:
            angle = 90
        elif direction[1] == 1:
            angle = 180
        else:
            angle = 0
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.x = x # (x,y) is the point at the front of the car, center between right and left
        self.rect.y = y
        #self.speed = random.randint(speed-5, speed+10)
        self.speed = speed
        self.turning = False # Set to True if car is turning
        self.turn_choice = random.randint(0,2) # Defines in which direction car wants to turn ->
                                                     # 0:forward, 1:right, 2:left

    def draw(self, screen):
        if self.direction[0] == 1:
            x = self.rect.x - self.side_length + self.front_buffer
            y = self.rect.y - self.side_length/2
        elif self.direction[0] == -1:
            x = self.rect.x - self.front_buffer
            y = self.rect.y - self.side_length / 2
        elif self.direction[1] == 1:
            y = self.rect.y - self.side_length + self.front_buffer
            x = self.rect.x - self.side_length / 2
        else:
            y = self.rect.y - self.front_buffer
            x = self.rect.x - self.side_length / 2
        screen.blit(self.image, (x, y))

    def drive(self, go):
        if go:
            if self.turning:
                self.turn()
            else:
                self.rect.x += self.direction[0] * self.speed
                self.rect.y += self.direction[1] * self.speed
                print(self.rect.y)
                if self.direction[1] == 0 and 435 < self.rect.x < 565: #Check if turning phase is triggered (x)
                    self.turning = True
                if self.direction[0] == 0 and 435 < self.rect.y < 565: #Check if turning phase is triggered (y)

                    self.turning = True


    def turn(self):
        pass # animate turning

