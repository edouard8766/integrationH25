import random
from enum import Enum
from dataclasses import dataclass, astuple
from typing import ClassVar, Optional
from math import pi, isclose, cos, sin, sqrt, atan, isinf

LANE_WIDTH = 3.6

def arclength(a: float, b: float) -> float:
    a, b = abs(a), abs(b)
    return pi/4 * (3 * (a + b) - sqrt((3 * a + b) * (a + 3 * b)))

def clamp[T](n: T, a: T, b: T) -> T:
    return max(a, min(n, b))


class Direction(Enum):
    North = 1
    South = 2
    East = 3
    West = 4

    @property
    def rad(self):
        match self:
            case Direction.North:
                return pi / 2
            case Direction.East:
                return 0.
            case Direction.South:
                return 3 * pi / 2
            case Direction.West:
                return pi

    @property
    def left(self):
        match self:
            case Direction.North:
                return Direction.West
            case Direction.East:
                return Direction.North
            case Direction.South:
                return Direction.East
            case Direction.West:
                return Direction.South
    @property
    def right(self):
        match self:
            case Direction.North:
                return Direction.East
            case Direction.East:
                return Direction.South
            case Direction.South:
                return Direction.West
            case Direction.West:
                return Direction.North

    @property
    def opposite(self):
        match self:
            case Direction.North:
                return Direction.South
            case Direction.East:
                return Direction.West
            case Direction.South:
                return Direction.North
            case Direction.West:
                return Direction.East


@dataclass
class Position:
    x: float = 0.
    y: float = 0.

    def __iter__(self):
        return iter(astuple(self))

    def offset(self, direction: Direction, distance: float) -> 'Position':
        x = self.x
        y = self.y
        match direction:
            case Direction.East:
                x += distance
            case Direction.West:
                x -= distance
            case Direction.North:
                y -= distance
            case Direction.South:
                y += distance

        return Position(x, y)

    def map(self, origin: 'Viewport', screen: 'Viewport') -> 'Position':
        return Position(
            self.x * screen.width/origin.width,
            self.y * screen.height/origin.height
        )

    def __add__(self, other: 'Position'):
        if not isinstance(other, Position):
            return NotImplemented
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Position'):
        if not isinstance(other, Position):
            return NotImplemented
        return Position(self.x - other.x, self.y - other.y)


@dataclass
class Transform:
    position: Position
    rotation: float = 0.

    def map(self, origin: 'Viewport', screen: 'Viewport') -> 'Transform':
        return Transform(
            Position(
                self.position.x * screen.width/origin.width,
                self.position.y * screen.height/origin.height
            ),
            self.rotation
        )


class TrafficSignal(Enum):
    Permitted = 1
    Protected = 2
    Halt = 3


class TrafficSignalPhase(Enum):
    EastWestPermitted = 1
    EastProtected = 2
    WestProtected = 3
    NorthSouthPermitted = 4
    NorthProtected = 5
    SouthProtected = 6

    def signal_at(self, direction: Direction) -> TrafficSignal:
        match (self, direction):
            case (TrafficSignalPhase.EastWestPermitted, Direction.East | Direction.West):
                return TrafficSignal.Permitted
            case (TrafficSignalPhase.EastProtected, Direction.East):
                return TrafficSignal.Protected
            case (TrafficSignalPhase.WestProtected, Direction.West):
                return TrafficSignal.Protected
            case (_, Direction.West) | (_, Direction.East):
                return TrafficSignal.Halt
                
            case (TrafficSignalPhase.NorthSouthPermitted, Direction.North | Direction.South):
                return TrafficSignal.Permitted
            case (TrafficSignalPhase.NorthProtected, Direction.North):
                return TrafficSignal.Protected
            case (TrafficSignalPhase.SouthProtected, Direction.South):
                return TrafficSignal.Protected
            case (_, Direction.South) | (_, Direction.North):
                return TrafficSignal.Halt


@dataclass
class Road:
    direction: Direction
    length: float
    start: Position
    lanes: int = 2

    def start_at(self, lane: int):
        return self.start.offset(self.direction.right, LANE_WIDTH * lane)

    @property
    def end(self):
        return self.start.offset(self.direction, self.length)

    def end_at(self, lane: int):
        return self.end.offset(self.direction.right, LANE_WIDTH * lane)


@dataclass
class Lane:
    road: Road
    lane: int = 0

    @property
    def start(self):
        return self.road.start_at(self.lane)

    @property
    def end(self):
        return self.road.end_at(self.lane)


class CarIntention(Enum):
    Continue = 1
    TurnLeft = 2
    TurnRight = 3


@dataclass
class Car:
    speed: float
    target_speed: float
    intention: CarIntention

    MAX_ACCELERATION: ClassVar[float] = 10.
    MAX_DECELERATION: ClassVar[float] = -10.

    def step(self, obstacle: Optional[tuple[float, float]], delta_time: float) -> float:
        acceleration = 0.

        if obstacle is not None:
            obstacle_distance, obstacle_velocity = obstacle
            if obstacle_distance <= 0.:
                acceleration = self.MAX_DECELERATION
            else:
                relative_velocity = self.speed - obstacle_velocity

                if relative_velocity > 0.:
                    acceleration = max(
                            (obstacle_velocity ** 2 - self.speed ** 2)
                                / (2. * obstacle_distance),
                            self.MAX_DECELERATION
                    )
                else:
                    acceleration = self.MAX_ACCELERATION
        elif self.speed < self.target_speed:
            acceleration = self.MAX_ACCELERATION
        elif self.speed > self.target_speed:
            acceleration = self.MAX_DECELERATION

        self.speed = clamp(
                self.speed + acceleration * delta_time,
                0., self.target_speed
        )

        return self.speed * delta_time


@dataclass
class CarRecord:
    car: Car
    distance: float
    lane: Optional[Lane]
    transition: Optional[tuple[Lane, Lane]]
    emissions: float = 0.

    @property
    def intention(self):
        return self.car.intention

    @property
    def speed(self):
        return self.car.speed

    @property
    def road(self) -> Optional[Road]:
        if self.lane is not None:
            return self.lane.road
        else:
            return None

    @property
    def max_distance(self):
        if self.lane is not None:
            return self.lane.road.length
        if self.transition is not None:
            approach, destination = self.transition
            a = approach.end
            b = destination.start

            s = abs((a - b).x)
            h = abs((b - a).y)

            if isclose(s, 0.):
                return h
            elif isclose(h, 0.):
                return s
            elif isclose(s, h):
                return pi * s / 2
            return arclength(s, h)
        return float('inf')


    @property
    def is_out_of_bounds(self):
        return self.distance > self.max_distance

    @property
    def transform(self) -> Optional[Transform]:
        if self.lane is not None:
            position = self.lane.start.offset(self.road.direction, self.distance)
            rotation = self.road.direction.rad
            return Transform(position, rotation)
        elif self.transition is not None:
            approach, destination = self.transition
            if approach.road.direction == destination.road.direction.opposite:
                #  Cannot perform U-Turn
                return None

            a = approach.end
            b = destination.start

            s = (a - b).x
            h = (b - a).y

            position = 0.
            rotation = 0.

            is_right_turn = approach.road.direction.right == destination.road.direction
            is_negative_product = s * h <= 0

            if approach.road.direction == destination.road.direction:
                match approach.road.direction:
                    case Direction.North:
                        position = a - Position(y=self.distance)
                    case Direction.South:
                        position = a + Position(y=self.distance)
                    case Direction.East:
                        position = a + Position(x=self.distance)
                    case Direction.West:
                        position = a - Position(x=self.distance)
                rotation = approach.road.direction.rad
            # elif isclose(abs(s), abs(h), rel_tol=.001):
            else:
                θ = self.distance / abs(s)

                if approach.road.direction in (Direction.South, Direction.North):
                    position = Position(s*cos(θ) - s, h * sin(θ)) + a
                    if is_right_turn:
                        if approach.road.direction == Direction.North:
                            rotation = pi / 2 - θ
                        else:
                            rotation = 3*pi / 2 - θ
                    else:
                        if approach.road.direction == Direction.North:
                            rotation = θ - 3*pi / 2
                        else:
                            rotation = θ - pi / 2
                else:
                    position = a - Position(s * sin(θ), h * cos(θ) - h)
                    if is_right_turn:
                        if approach.road.direction == Direction.East:
                            rotation = 2*pi - θ
                        else:
                            rotation = pi - θ
                    else:
                        if approach.road.direction == Direction.East:
                            rotation = 2*pi + θ
                        else:
                            rotation = pi + θ


                #if (is_right_turn and is_negative_product) \
                #   or (not is_right_turn and not is_negative_product):
                #    position = Position(s * cos(θ) - s, h * sin(θ)) + a
                #    if is_right_turn:
                #        rotation = θ
                #    else:
                #        rotation = 2 * pi - θ
                #else:
                #    position = a - Position(s * sin(θ), h * cos(θ) - h)
                #    if is_right_turn:
                #        rotation = θ
                #    else:
                #        rotation = 2 * pi - θ
            # else:
            #     L = arclength(s, h)
            #     θ = pi * self.distance / (2 * L)

            #     if (is_right_turn and is_negative_product) \
            #        or (not is_right_turn and not is_negative_product):
            #         position = Position(s * cos(θ) - s, h * sin(θ)) + a
            #         dx = -s * sin(θ)
            #         dy = h * cos(θ)
            #         rotation = 2 * pi - atan(dy/dx)
            #     else:
            #         position = a - Position(s * sin(θ), h * cos(θ) - h)
            #         dx = s * cos(θ)
            #         dy = -h * sin(θ)
            #         if dx != 0:
            #             rotation = atan(dy/dx)
            #         else:
            #             rotation = approach.road.direction.rad
            #     #  position = Position(s * cos(θ) - s, h * sin(θ)) + a
            #     #  dx = -s * sin(θ)
            #     #  dy =  h * cos(θ)
            #     #  rotation =  atan(dy/dx)

            return Transform(position, rotation)
        else:
            return None

    def step(self, obstacle: Optional[tuple[float, float]], delta_time: float):
        previous_speed = self.speed

        self.distance += self.car.step(obstacle, delta_time)

        if self.speed > previous_speed:
            self.emissions += 0.0002083 * (self.speed ** 2 - previous_speed ** 2)



@dataclass
class Viewport:
    width: float
    height: float

    def __iter__(self):
        return iter(astuple(self))

    @property
    def top_left(self) -> Position:
        return Position(0., 0.)

    @property
    def top_middle(self) -> Position:
        return Position(self.width / 2., 0.)

    @property
    def top_right(self) -> Position:
        return Position(self.width, 0.)

    @property
    def bottom_left(self) -> Position:
        return Position(0., self.height)

    @property
    def bottom_middle(self) -> Position:
        return Position(self.width / 2., self.height)

    @property
    def bottom_right(self) -> Position:
        return Position(self.width, self.height)

    @property
    def horizon_left(self) -> Position:
        return Position(0., self.height / 2.)

    @property
    def horizon_middle(self) -> Position:
        return Position(self.width / 2., self.height / 2.)

    @property
    def horizon_right(self) -> Position:
        return Position(self.width, self.height / 2.)
    
    @property
    def center(self) -> Position:
        return self.horizon_middle


class IntersectionSimulation:
    #  width, height in meters
    VIEWPORT: ClassVar[Viewport] = Viewport(100, 100)

    WEST_EAST: ClassVar[Road] = Road(
        direction = Direction.East,
        length = VIEWPORT.center.x - 3. * LANE_WIDTH, 
        start = VIEWPORT.horizon_left + Position(y=LANE_WIDTH/3)
    )

    WEST_WEST: ClassVar[Road] = Road(
        direction = Direction.West,
        length = VIEWPORT.center.x - 3. * LANE_WIDTH,
        start = VIEWPORT.center - Position(3 * LANE_WIDTH, LANE_WIDTH/3)
    )

    NORTH_NORTH: ClassVar[Road] = Road(
        direction = Direction.North,
        length = VIEWPORT.center.y - 3. * LANE_WIDTH,
        start = VIEWPORT.center + Position(LANE_WIDTH/3, -3. * LANE_WIDTH)
    )

    NORTH_SOUTH: ClassVar[Road] = Road(
        direction = Direction.South,
        length = VIEWPORT.center.y - 3. * LANE_WIDTH,
        start = VIEWPORT.top_middle - Position(x=LANE_WIDTH/3)
    )

    EAST_WEST: ClassVar[Road] = Road(
        direction = Direction.West,
        length = VIEWPORT.center.x - 3. * LANE_WIDTH,
        start = VIEWPORT.horizon_right - Position(y=LANE_WIDTH/3)
    )

    EAST_EAST: ClassVar[Road] = Road(
        direction = Direction.East,
        length = VIEWPORT.center.x - 3. * LANE_WIDTH,
        start = VIEWPORT.center + Position(3 * LANE_WIDTH, LANE_WIDTH/3)
    )

    SOUTH_NORTH: ClassVar[Road] = Road(
        direction = Direction.North,
        length = VIEWPORT.center.y - 3. * LANE_WIDTH,
        start = VIEWPORT.bottom_middle + Position(x=LANE_WIDTH/3)
    )

    SOUTH_SOUTH: ClassVar[Road] = Road(
        direction = Direction.South,
        length = VIEWPORT.center.y - 3. * LANE_WIDTH,
        start = VIEWPORT.center - Position(LANE_WIDTH/3, -3. * LANE_WIDTH)
    )


    def __init__(self, phase = TrafficSignalPhase.EastWestPermitted):
        self.cars: list[CarRecord] = []
        self.phase = phase
        self.previous_phase = phase
        self.delta_emissons = 0.

    def spawn_car(self, car: Car, direction: Direction):
        road = self.approach_road(direction)
        lane: Lane
        match car.intention:
            case CarIntention.Continue:
                lane = Lane(road, lane=1)
            case CarIntention.TurnLeft:
                lane = Lane(road, lane=0)
            case CarIntention.TurnRight:
                lane = Lane(road, lane=road.lanes - 1)
        car_record = CarRecord(car, distance=0., lane=lane, transition=None)
        self.cars.append(car_record)

    def approach_road(self, direction: Direction) -> Road:
        match direction:
            case Direction.North:
                return self.NORTH_SOUTH
            case Direction.East:
                return self.EAST_WEST
            case Direction.South:
                return self.SOUTH_NORTH
            case Direction.West:
                return self.WEST_EAST

    def destination_road(self, direction: Direction) -> Road:
        match direction:
            case Direction.North:
                return self.NORTH_NORTH
            case Direction.East:
                return self.EAST_EAST
            case Direction.South:
                return self.SOUTH_SOUTH
            case Direction.West:
                return self.WEST_WEST
        

    def __next_car_in_lane(self, target: CarRecord) -> Optional[CarRecord]:
        return min(
            (
                car for car in self.cars
                if (car.lane is not None 
                    and car.lane == target.lane
                    and car is not target
                    and isinstance(car.distance, float) 
                    and not isinf(car.distance)
                    and car.distance >= target.distance)
            ),
            key=lambda car: car.distance,
            default=None
        )

    def is_entry_possible(self, intention: CarIntention, approach: Direction):
        approach_signal = self.phase.signal_at(approach)

        match (intention, approach_signal):
            case (CarIntention.Continue | CarIntention.TurnRight,
                  TrafficSignal.Permitted | TrafficSignal.Protected):
                return True
            case (CarIntention.TurnLeft, TrafficSignal.Protected):
                return True
            case _:
                return False

    @property
    def emissions(self):
        return sum(car.emissions for car in self.cars)

    def step(self, delta_time: float):
        previous_emissions = self.emissions

        for car_record in self.cars:
            obstacle: Optional[tuple[float, float]] = None

            next_car = self.__next_car_in_lane(car_record)

            if next_car is not None:
                obstacle = next_car.distance - car_record.distance, next_car.speed
            elif car_record.lane is not None and car_record.road is self.approach_road(car_record.road.direction):
                approach = car_record.road.direction.opposite
                if not self.is_entry_possible(car_record.intention, approach):
                    obstacle = car_record.road.length - car_record.distance, 0.

            car_record.step(obstacle, delta_time)

            if car_record.is_out_of_bounds:
                car_record.distance %= car_record.max_distance
                if car_record.transition is not None:
                    _, next_lane = car_record.transition
                    car_record.lane = next_lane
                    car_record.transition = None
                elif car_record.road == self.approach_road(car_record.road.direction.opposite):
                    next_lane: Lane
                    match car_record.intention:
                        case CarIntention.Continue:
                            next_road = self.destination_road(car_record.road.direction)
                            next_lane = Lane(next_road, car_record.lane.lane)
                        case CarIntention.TurnLeft:
                            next_road = self.destination_road(car_record.road.direction.left)
                            next_lane = Lane(next_road)
                        case CarIntention.TurnRight:
                            next_road = self.destination_road(car_record.road.direction.right)
                            next_lane = Lane(next_road, next_road.lanes - 1)
                    car_record.transition = car_record.lane, next_lane
                    car_record.lane = None
                else:
                    self.cars.remove(car_record)

        self.delta_emissions = self.emissions - previous_emissions

    def take_action(self): # simulate dqn action for simtest.py
        random_phase = random.choice(list(TrafficSignalPhase))
        self.previous_phase = self.phase
        self.phase = self.phase = random_phase



