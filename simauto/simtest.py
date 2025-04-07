from sim import IntersectionSimulation, Car, CarIntention, Direction, TrafficSignalPhase
import pygame
import os
import math
from trafficLights import TrafficLight

current_dir = os.path.dirname(os.path.abspath(__file__))


def draw_item(screen, image, pos):
    screen.blit(image, pos)

def set_lights_color(lights_status, traffic_lights):
    if lights_status.value == TrafficSignalPhase.NorthSouthPermitted.value:
        traffic_lights[3].set_state(0)  # south-north
        traffic_lights[2].set_state(0)  # nort-south
        traffic_lights[1].set_state(2)  # east-west
        traffic_lights[0].set_state(2)  # west-east
    elif lights_status.value == TrafficSignalPhase.SouthProtected.value:
        traffic_lights[3].set_state(3)
        traffic_lights[2].set_state(2)
        traffic_lights[1].set_state(2)
        traffic_lights[0].set_state(2)
    elif lights_status.value == TrafficSignalPhase.NorthProtected.value:
        traffic_lights[3].set_state(2)
        traffic_lights[2].set_state(3)
        traffic_lights[1].set_state(2)
        traffic_lights[0].set_state(2)
    elif lights_status.value == TrafficSignalPhase.EastWestPermitted.value:
        traffic_lights[3].set_state(2)
        traffic_lights[2].set_state(2)
        traffic_lights[1].set_state(0)
        traffic_lights[0].set_state(0)
    elif lights_status.value == TrafficSignalPhase.WestProtected.value:
        traffic_lights[3].set_state(2)
        traffic_lights[2].set_state(2)
        traffic_lights[1].set_state(2)
        traffic_lights[0].set_state(3)
    elif lights_status.value == TrafficSignalPhase.EastProtected.value:
        traffic_lights[3].set_state(2)
        traffic_lights[2].set_state(2)
        traffic_lights[1].set_state(3)
        traffic_lights[0].set_state(2)
    else:
        traffic_lights[3].set_state(2)
        traffic_lights[2].set_state(2)
        traffic_lights[1].set_state(2)
        traffic_lights[0].set_state(2)

def set_yellow_lights(new_state, yellow_counter, lights_status, yellow_duration, traffic_lights):
    if new_state in (0, 3):
        if lights_status in (
        new_state + 1, new_state + 2):  # if light_status goes from blinking_green to green in same axis
            return False # No yellow light

    if lights_status == TrafficSignalPhase.NorthSouthPermitted.value:
        if new_state == 1:
            traffic_lights[2].set_state(1)
        elif new_state == 2:
            traffic_lights[3].set_state(1)
        else:
            traffic_lights[2].set_state(1)  # Set color to yellow
            traffic_lights[3].set_state(1)
    elif lights_status == TrafficSignalPhase.SouthProtected.value:
        traffic_lights[3].set_state(1)
    elif lights_status == TrafficSignalPhase.NorthProtected.value:
        traffic_lights[2].set_state(1)
    elif lights_status == TrafficSignalPhase.EastWestPermitted.value:
        if new_state == 4:
            traffic_lights[1].set_state(1)
        elif new_state == 5:
            traffic_lights[0].set_state(1)
        else:
            traffic_lights[0].set_state(1)
            traffic_lights[1].set_state(1)
    elif lights_status == TrafficSignalPhase.WestProtected.value:
        traffic_lights[0].set_state(1)
    elif lights_status == TrafficSignalPhase.EastProtected.value:
        traffic_lights[1].set_state(1)
    return True # Yellow light on

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
    yellow_light_on = False
    yellow_duration = 3.5
    yellow_counter = yellow_duration

    for i in range(0, 4):
        traffic_lights.append(TrafficLight(i, 2))

    while running:
        #Check for events
        for event in pygame.event.get():
            if (event.type == pygame.QUIT or
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
                running = False

        #Render background
        screen.blit(background, (0, 0))

        # Render traffic lights
        if yellow_light_on:
            yellow_counter -= 1
            if yellow_counter < 0:
                yellow_light_on = False
                set_lights_color(simulation.phase, traffic_lights)
        else:
            set_lights_color(simulation.phase, traffic_lights)

        for light in traffic_lights:
            light.draw(screen)
        print(simulation.phase)


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
