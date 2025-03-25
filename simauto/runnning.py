import gymnasium as gym

from intersection import IntersectionEnv

#init env
steps_per_second = 0.25
env = IntersectionEnv(steps_per_second)
#reset and start

obs, info = env.reset()
running = True

while running:
    if env.frame_counter % env.fps/steps_per_second == 0:
        if not env.yellow_light_on:
            action = env.action_space.sample() #action random jsp quoi mettre pour l'instant
            obs, reward, terminated, truncated, info = env.step(action)
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