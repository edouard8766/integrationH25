import pygame
import random
import math

class DrivingCar(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, direction):
        pygame.sprite.Sprite.__init__(self)
        filename = "items\Car" + str(random.randint(0,0)) + ".png"
        self.image = pygame.image.load(filename)
        self.image = pygame.transform.scale(self.image, (165,165))
        self.direction = direction
        if direction[0] == 1:
            angle = 0
        elif direction[0] == -1:
            angle = 180
        elif direction[1] == 1:
            angle = 90
        else:
            angle = 270
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = random.randint(speed-5, speed+10)

    def draw(self, screen):
        screen.blit(self.image, self.rect)