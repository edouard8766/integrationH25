import gymnasium as gym

from intersection import IntersectionEnv

#init env
env = IntersectionEnv()
#reset and start

obs, info = env.reset()
running = True

while running:
    action = 3 #env.action_space.sample() #action random jsp quoi mettre pour l'instant
    obs, reward, terminated, truncated, info = env.step(action)
    env.render()

    if terminated or truncated:
        running = False
        env.close()

env.close()