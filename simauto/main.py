pixlimport math
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
icon = pygame.image.load("items\Icon.png")
pygame.display.set_icon(icon)

pygame.mixer.music.load("items\Music.mp3")
pygame.mixer.music.play(-1)

run = True
drive = False
class Background(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("items\Background.png")
        self.image = pygame.transform.scale(self.image, (1000,1000))

    def draw(self):
        screen.blit(self.image, (0,0))

background = Background()
car = cars.DrivingCar(200, 485, 2, (1,0))
'''
Possible starting pos:
dir[1,0] -> (0,452), (0,485)
dir[-1,0] -> (screenWidth+car_length,452), (screeWidth+car_length,485)
dir[0,1] -> (452,0), (485,0)
dir[0,-1] -> (452,screenHeight+car_length), (485,screeHeight+car_length)
'''

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