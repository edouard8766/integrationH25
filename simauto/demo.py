import gymnasium as gym
import simauto.register_env
from dqn import *  # This should include your DeepQNetwork and ReplayBuffer if needed
from simauto.agent import DQNAgent, state_tensor
import os

device = T.device("cuda" if T.cuda.is_available() else "cpu")

# Create environment and agent
env = gym.make("Intersection-v0", render_mode="human", step_length=0.25)
input_dim = 4 + 4  # pressure + nearest
output_dim = 6
agent = DQNAgent(input_dim, output_dim)
agent.load("model0.txt")  # Load the trained model

# Disable exploration for demo
agent.epsilon = 0.0

# Run one episode for demo
obs, _ = env.reset()
state = state_tensor(obs)
done = False

step = 0
action = 0

while not done:
    action = agent.act(state)
    next_obs, reward, terminated, truncated, _ = env.step(action)
    state = state_tensor(next_obs)
    env.render()
    done = truncated
    step += 1

sum = 0
mean_waits = env.unwrapped.mean_waits
for w in mean_waits:
    sum += w
mean_wait = sum / len(mean_waits)
print(mean_wait)
print(env.unwrapped.sim.emissions)

env.close()
