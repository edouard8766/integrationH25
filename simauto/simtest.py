from typing import ClassVar

from sim import IntersectionSimulation, Car, CarIntention, Direction, TrafficSignalPhase, Viewport, LANE_WIDTH
import pygame
import os
import math
from trafficLights import TrafficLight

class Asset:
    ASSET_PATH: ClassVar[str] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

    @classmethod
    def load(cls, asset_name: str):
        return pygame.image.load(os.path.join(cls.ASSET_PATH, asset_name))

def draw_item(screen, sprite, pos):
    screen.blit(sprite, pos)

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
    pygame.init()
    viewport = Viewport(500, 500)
    screen = pygame.display.set_mode((viewport.width, viewport.height))
    pygame.display.set_caption("Traffic Simulation")
    clock = pygame.time.Clock()
    fps = 30

    background_sprite = Asset.load("Background.png")
    background_sprite = pygame.transform.scale(background_sprite, (viewport.width, viewport.height))
    def draw_background(screen): screen.blit(background_sprite, (0, 0))

    car_sprite = Asset.load("Car0.png")
    car_sprite = pygame.transform.rotate(car_sprite, -90)
    car_sprite = pygame.transform.scale(car_sprite, (viewport.width/20, viewport.height/20))
    car_rect = pygame.Surface((viewport.width/30, viewport.width/45))
    car_rect.set_colorkey((0,0,0))
    car_rect.fill(pygame.Color("gold"))

    def draw_car(screen, car): 

        sprite = car_sprite
        rect_sprite = car_rect
        if car.transform.rotation != 0:
            sprite = pygame.transform.rotate(sprite, math.degrees(car.transform.rotation))
            rect_sprite = pygame.transform.rotate(rect_sprite, math.degrees(car.transform.rotation))

        position = car.transform.position.map(IntersectionSimulation.VIEWPORT, viewport)

        screen.blit(sprite, (position.x, position.y))
        screen.blit(rect_sprite, (position.x - rect_sprite.get_width() / 2  * math.sin(car.transform.rotation), position.y - rect_sprite.get_height() / 2 * math.cos(car.transform.rotation)))

    #TrafficLights
    traffic_lights = []
    yellow_light_on = False
    yellow_duration = 3.5
    yellow_counter = yellow_duration

    for i in range(0, 4):
        traffic_lights.append(TrafficLight(i, 2))

    running = True

    delta_time = 1/fps

    while running:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            running = False

        if len(simulation.cars) == 0:
            running = False

        draw_background(screen)

        #  Debug
        ROAD_START = IntersectionSimulation.WEST_EAST.start.map(
                IntersectionSimulation.VIEWPORT, viewport
        )

        ROAD_LENGTH = IntersectionSimulation.WEST_EAST.length * viewport.width / IntersectionSimulation.VIEWPORT.width


        ROAD_RECT = pygame.Rect((ROAD_START.x, ROAD_START.y), (ROAD_LENGTH, LANE_WIDTH * viewport.height / IntersectionSimulation.VIEWPORT.height))
        pygame.draw.rect(screen, pygame.Color("brown"), ROAD_RECT)


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


        #Cars update and render
        for car in simulation.cars:
            draw_car(screen, car)
            print("Transform:", car.transform)
            print("Road:", car.road)
            print("")

        simulation.step(delta_time)

        pygame.display.update()
        delta_time = clock.tick(fps) / 1000

if __name__ == '__main__':
    speed_limit = 10
    cars = [
        (
            Car(speed_limit, speed_limit, intention=CarIntention.TurnLeft),
            Direction.East
        )
    ]
    test(cars)
