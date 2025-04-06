from sim import IntersectionSimulation, Car, CarIntention, Direction


def test(cars):
    simulation = IntersectionSimulation()
    for car, direction in cars:
        simulation.spawn_car(car, direction)

    for i in range(100):
        print("Transform:", simulation.cars[0].transform)
        print("Road:", simulation.cars[0].road)
        print("")
        simulation.step(0.1)



if __name__ == '__main__':
    speed_limit = 10
    cars = [
        (
            Car(speed_limit, speed_limit, intention=CarIntention.TurnLeft),
            Direction.West
        )
    ]
    test(cars)
