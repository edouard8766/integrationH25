import os.path

import gymnasium as gym
import simauto.register_env  # must import to register the env
import torch as T
import numpy as np
import pickle
from dqn import *

def state_tensor(obs):
    return T.FloatTensor(np.concatenate([
        obs["pressure"].astype(np.float32),
        obs["nearest"].astype(np.float32),
        np.array(obs["lights"], dtype=np.float32)
    ]))

class DQNAgent:
    def __init__(self, input_dim, output_dim, gamma=0.99, epsilon=1.0, lr=0.001):
        self.q_net = DeepQNetwork(input_dim, output_dim)
        self.target_net = DeepQNetwork(input_dim, output_dim)
        self.optimizer = optim.Adam(self.q_net.parameters(), lr=lr)
        self.gamma = gamma
        self.epsilon = epsilon
        self.buffer = ReplayBuffer(max_size=100000)
        self.update_target_network()  # Initialize target = online

    def update_target_network(self):
        self.target_net.load_state_dict(self.q_net.state_dict())

    def act(self, state):
        if np.random.random() < self.epsilon:
            return np.random.randint(6)  # Random action
        else:
            with T.no_grad():
                q_values = self.q_net(state)
                return T.argmax(q_values).item()

    def save(self, path):
        T.save(self.q_net.state_dict(), path)

    def load(self, path):
        self.q_net.load_state_dict(T.load(path))

env = gym.make("Intersection-v0", render_mode="human", step_length=6.0)
input_dim = 4 + 4 + 6
output_dim = 6
agent = DQNAgent(input_dim, output_dim)

#Hyperparameters
BATCH_SIZE = 64
GAMMA = 0.99
EPSILON_DECAY = 0.992
MIN_EPSILON = 0.01
TARGET_UPDATE_FREQ = 100
episode_rewards = []
total_steps = 0
for episode in range(1000):
    obs, _ = env.reset()
    state = state_tensor(obs)
    total_reward = 0
    done = False

    while not done:
        action = agent.act(state)
        next_obs, reward, terminated, truncated, _ = env.step(action)
        next_state = state_tensor(next_obs)
        env.render()
        done = terminated or truncated

        agent.buffer.store(state.numpy(), action, reward, next_state.numpy(), done)
        state = next_state
        total_reward += reward
        env.sim.record_step_metrics(reward)
        # Train from buffer
        if len(agent.buffer.buffer) > BATCH_SIZE:
            states, actions, rewards, next_states, dones = agent.buffer.sample(BATCH_SIZE)
            states = T.FloatTensor(states)
            next_states = T.FloatTensor(next_states)

            # DQN Loss Calculation
            q_values = agent.q_net(states)
            next_q_values = agent.target_net(next_states).max(1)[0].detach()
            rewards_tensor = T.FloatTensor(rewards)
            dones_tensor = T.FloatTensor(dones)
            targets = rewards_tensor + (1 - dones_tensor) * agent.gamma * next_q_values

            loss = agent.q_net.loss(q_values.gather(1, T.LongTensor(actions).unsqueeze(1)), targets.unsqueeze(1))
            agent.optimizer.zero_grad()
            loss.backward()
            agent.optimizer.step()

            # Update target network
            total_steps += 1
            if total_steps % TARGET_UPDATE_FREQ == 0:
                agent.update_target_network()

    episode_rewards.append(total_reward)
    print(f"Episode {episode}, Reward: {total_reward:.2f}, Epsilon: {agent.epsilon:.2f}")
    agent.epsilon = max(MIN_EPSILON, agent.epsilon * EPSILON_DECAY)
    if episode % 10 == 0 or episode == 999:
        env.sim.save_metrics(f'simulation_episode_{episode}.pkl')
path = os.path.join("saved_models", "model0.txt")
agent.save(path)
env.close()
