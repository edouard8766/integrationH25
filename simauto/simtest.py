import time
from typing import ClassVar

from sim import IntersectionSimulation, Car, CarIntention, Direction, TrafficSignalPhase, Viewport, Transform, Lane, Position
import pygame
import os
import math
from trafficLights import TrafficLight

class Asset:
    ASSET_PATH: ClassVar[str] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

    @classmethod
    def load(cls, asset_name: str):
        return pygame.image.load(os.path.join(cls.ASSET_PATH, asset_name))

class Sprite:
    def __init__(self, surface):
        self.surface = surface

    def draw(self, screen, transform: Transform):
        rect = self.surface.get_rect(center=tuple(transform.position))
        surface = pygame.transform.rotate(self.surface, math.degrees(transform.rotation))
        screen.blit(surface, rect)


#  Pour debug
def draw_road(screen, road):
    screen_view = Viewport(screen.get_width(), screen.get_height())
    first_lane = Lane(road, 0)
    last_lane = Lane(road, road.lanes - 1)
    start = first_lane.start.map(IntersectionSimulation.VIEWPORT, screen_view)
    end = last_lane.end.map(IntersectionSimulation.VIEWPORT, screen_view)
    rect = pygame.Rect(tuple(start), tuple(end-start))
    rect1 = pygame.Rect(tuple(end), tuple(start-end))
    pygame.draw.rect(screen, pygame.Color("red"), rect)
    pygame.draw.rect(screen, pygame.Color("red"), rect1)

def draw_item(screen, sprite, pos):
    screen.blit(sprite, pos)

def set_lights_color(lights_status, traffic_lights):
    if lights_status.value == TrafficSignalPhase.NorthSouthPermitted.value:
        traffic_lights[3].set_state(0)  # south-north
        traffic_lights[2].set_state(0)  # north-south
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

def set_yellow_lights(new_state, lights_status, traffic_lights):
    if new_state in (1, 4):
        if lights_status in (new_state + 1, new_state + 2):
            return False  # No yellow light

    if lights_status == TrafficSignalPhase.NorthSouthPermitted:
        if new_state == TrafficSignalPhase.SouthProtected:
            traffic_lights[2].set_state(1)
        elif new_state == TrafficSignalPhase.NorthProtected:
            traffic_lights[3].set_state(1)
        else:
            traffic_lights[2].set_state(1)
            traffic_lights[3].set_state(1)
    elif lights_status == TrafficSignalPhase.SouthProtected:
        traffic_lights[3].set_state(1)
    elif lights_status == TrafficSignalPhase.NorthProtected:
        traffic_lights[2].set_state(1)
    elif lights_status == TrafficSignalPhase.EastWestPermitted:
        if new_state == TrafficSignalPhase.WestProtected:
            traffic_lights[1].set_state(1)
        elif new_state == TrafficSignalPhase.EastProtected:
            traffic_lights[0].set_state(1)
        else:
            traffic_lights[0].set_state(1)
            traffic_lights[1].set_state(1)
    elif lights_status == TrafficSignalPhase.WestProtected:
        traffic_lights[0].set_state(1)
    elif lights_status == TrafficSignalPhase.EastProtected:
        traffic_lights[1].set_state(1)
    return True

def test(cars, speed_multiplier=1):
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

    car_rect_sprite = Sprite(car_rect)
    def draw_car(screen, car):
        sprite = car_sprite
        rect_sprite = car_rect
        if car.transform.rotation != 0:
            sprite = pygame.transform.rotate(sprite, math.degrees(car.transform.rotation))
            rect_sprite = pygame.transform.rotate(rect_sprite, math.degrees(car.transform.rotation))

        position = car.transform.position.map(IntersectionSimulation.VIEWPORT, viewport)
        screen.blit(sprite, (position.x, position.y))
        screen.blit(rect_sprite, (
            position.x - rect_sprite.get_width() / 2 * math.sin(car.transform.rotation),
            position.y - rect_sprite.get_height() / 2 * math.cos(car.transform.rotation)
        ))

    traffic_lights = [TrafficLight(i, 2) for i in range(4)]
    yellow_light_on = False
    yellow_duration = 3.5 / speed_multiplier
    yellow_counter = yellow_duration

    running = True
    delta_time = 1 / fps
    last_phase_change = time.time()
    a_bool_to_be_used_only_once = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False

        if len(simulation.cars) == 0:
            running = False

        draw_background(screen)

        # Debug visuals
        ROAD_START = IntersectionSimulation.WEST_EAST.start.map(
            IntersectionSimulation.VIEWPORT, viewport
        )
        ROAD_LENGTH = IntersectionSimulation.WEST_EAST.length * viewport.width / IntersectionSimulation.VIEWPORT.width
        ROAD_RECT = pygame.Rect(
            (ROAD_START.x, ROAD_START.y),
            (ROAD_LENGTH, LANE_WIDTH * viewport.height / IntersectionSimulation.VIEWPORT.height)
        )
        pygame.draw.rect(screen, pygame.Color("brown"), ROAD_RECT)

        if a_bool_to_be_used_only_once:
            set_lights_color(simulation.phase, traffic_lights)
            a_bool_to_be_used_only_once = False
        # Handle traffic lights
        now = time.time()
        # Render traffic lights
        if yellow_light_on:
            yellow_counter -= delta_time
            if yellow_counter <= 0:
                yellow_light_on = False
                set_lights_color(simulation.phase, traffic_lights)
                last_phase_change = now
        else:
            if now - last_phase_change >= 4 / speed_multiplier:  # change cycle time here
                simulation.take_action()  # picks a new phase

                if set_yellow_lights(simulation.phase, simulation.previous_phase, traffic_lights):
                    yellow_light_on = True
                    yellow_counter = yellow_duration
                    last_phase_change = now
                else:
                    set_lights_color(simulation.phase, traffic_lights)
                    last_phase_change = now

        # Draw lights
        for light in traffic_lights:
            light.draw(screen)

        # Update and draw cars
        for car in simulation.cars:
            car_rect_sprite.draw(screen, car.transform.map(IntersectionSimulation.VIEWPORT, viewport))
            print("Transform:", car.transform)
            print("Road:", car.road)
            print("")

        simulation.step(delta_time)

        pygame.display.update()
        delta_time = (clock.tick(fps) / 1000) * speed_multiplier

if __name__ == '__main__':
    speed_limit = 10
    cars = [
        (
            Car(speed_limit, speed_limit, intention=CarIntention.TurnRight),
            Direction.East
        ),
        (
            Car(speed_limit, speed_limit, intention=CarIntention.Continue),
            Direction.North
        ),
        (
            Car(speed_limit, speed_limit, intention=CarIntention.Continue),
            Direction.South
        ),
        (
            Car(speed_limit, speed_limit, intention=CarIntention.TurnLeft),
            Direction.West
        ),
    ]
    test(cars, 1)
