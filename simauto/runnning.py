import gymnasium as gym
from car import Car, CarIntention
from intersection import IntersectionEnv

#init env
delta_time = 1 #steps/sec
env = IntersectionEnv(delta_time)
#reset and start

cars = [
    Car(target_speed=50, speed=50, intention=CarIntention.CONTINUE),
    Car(target_speed=50, speed=10, intention=CarIntention.TURN_LEFT),
]
obs, info = env.reset()
running = True

while running:
    if env.frame_counter % (env.fps/delta_time) == 0:
        if not env.yellow_light_on:
            action = env.action_space.sample() #action random jsp quoi mettre pour l'instant
            obs, reward, terminated, truncated, info = env.step(action)

            for car in cars:
                crossed_line = env.check_intersection_cross(car)
                distance_moved = car.step(stop_distance=None, delta_time=delta_time)
            if terminated or truncated:
                running = False
                env.close()
                break
    else:
        if env.truncated:
            running = False
            env.close()
            break
    env.render()

env.close()