# agent.py
import torch as T
import torch.nn as nn
import torch.optim as optim
import numpy as np
from dqn import DeepQNetwork, ReplayBuffer  # make sure these are in dqn.py

device = T.device("cuda" if T.cuda.is_available() else "cpu")

def state_tensor(obs):
    return T.FloatTensor(np.concatenate([
        obs["pressure"].astype(np.float32),
        obs["nearest"].astype(np.float32),
    ])).to(device)

class DQNAgent:
    def __init__(self, input_dim, output_dim, gamma=0.99, epsilon=1.0, lr=0.001):
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
        if np.random.random() < self.epsilon:
            return np.random.randint(6)
        else:
            with T.no_grad():
                q_values = self.q_net(state)
                return T.argmax(q_values).item()

    def save(self, path):
        T.save(self.q_net.state_dict(), path)

    def load(self, path):
        self.q_net.load_state_dict(T.load(path, map_location=device))
