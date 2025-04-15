import gymnasium as gym
import simauto.register_env  # must import to register the env

env = gym.make("Intersection-v0", render_mode="human", step_length=1.0)
obs, info = env.reset()

done = False
while not done:
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
    print(f"Reward: {reward:.2f}")

env.close()
