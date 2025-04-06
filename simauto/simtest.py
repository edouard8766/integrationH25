from sim import IntersectionSimulation, Car, CarIntention, Direction
import pygame
import os
import math
#from trafficLights import TrafficLight

current_dir = os.path.dirname(os.path.abspath(__file__))


def draw_item(screen, image, pos):
    screen.blit(image, pos)

def test(cars):
    simulation = IntersectionSimulation()
    for car, direction in cars:
        simulation.spawn_car(car, direction)

    #pygame
    running = True
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    pygame.display.set_caption("Traffic Simulation")
    clock = pygame.time.Clock()
    fps = 30
    #Background
    background = pygame.image.load(os.path.join(current_dir, "assets", "Background.png"))
    background = pygame.transform.scale(background, (1000, 1000))
    #Car image
    car_img = pygame.image.load(os.path.join(current_dir, "assets", "Car0.png"))
    car_img = pygame.transform.scale(car_img, (50, 50))
    #TrafficLights
    traffic_lights = []
    #for i in range(0, 4):
        #traffic_lights.append(TrafficLight(i, 2))

    while running:
        #Check for events
        for event in pygame.event.get():
            if (event.type == pygame.QUIT or
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
                running = False

        #Render background
        screen.blit(background, (0, 0))

        #Cars update and render
        for car in simulation.cars:
            pos = (car.transform.position.x, car.transform.position.y)
            img = pygame.transform.rotate(car_img, math.degrees(car.transform.rotation)-90)
            draw_item(screen, img, pos)
            print("Transform:", car.transform)
            print("Road:", car.road)
            print("")
        simulation.step(0.2)

        pygame.display.update()
        clock.tick(fps)  # 30 fps?




if __name__ == '__main__':
    speed_limit = 10
    cars = [
        (
            Car(speed_limit, speed_limit, intention=CarIntention.TurnRight),
            Direction.West
        )
    ]
    test(cars)
