import torch as T
import torch.nn as nn
import torch.optim as optim
import numpy as np
from dqn import DeepQNetwork, ReplayBuffer  # make sure these are in dqn.py
import gymnasium as gym
from gymnasium.spaces.utils import flatten_space, flatdim

device = T.device("cuda" if T.cuda.is_available() else "cpu")

class DQNAgent:
    def __init__(self, env: gym.Env, gamma=0.99, epsilon=0.0, lr=0.001):
        input_dim = flatdim(flatten_space(env.observation_space))
        output_dim = flatdim(flatten_space(env.action_space))
        self.action_space = env.action_space
        self.q_net = DeepQNetwork(input_dim, output_dim).to(device)
        self.target_net = DeepQNetwork(input_dim, output_dim).to(device)
        self.optimizer = optim.Adam(self.q_net.parameters(), lr=lr)
        self.gamma = gamma
        self.epsilon = epsilon
        self.buffer = ReplayBuffer(max_size=25000)
        self.update_target_network()

    def update_target_network(self):
        self.target_net.load_state_dict(self.q_net.state_dict())

    def act(self, state):
        state.to(device)
        if np.random.random() < self.epsilon:
            return self.action_space.sample()
        else:
            with T.no_grad():
                q_values = self.q_net(state)
                return T.argmax(q_values).item()

    def save(self, path):
        T.save(self.q_net.state_dict(), path)

    def load(self, path):
        self.q_net.load_state_dict(T.load(path, map_location=device))
