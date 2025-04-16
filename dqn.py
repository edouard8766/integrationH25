import numpy as np
import torch as T
import torch.nn as nn# torch neural network
import torch.nn.functional as F
import torch.optim as optim
import random
from collections import deque

from main import state_tensor

input_dim = 4 + 4 + 6# dans le dico pressure(4), nearest(4), lights(6)
output_dim = 0
class ReplayBuffer:
    def __init__(self, max_size):
        self.buffer = deque(maxlen=max_size) #on fix la size en utilisant deque, max_size c'est la capacite

    def store(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done)) # on save,  jsp si ca marche mais le gars le fait de meme

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size) # on sample random
        states, actions, rewards, next_states, dones = map(np.array, zip(*batch))
        return states, actions, rewards, next_states, dones

class DeepQNetwork(nn.Module):

    def __init__(self, input_dim, output_dim): # maybe faut mettre d'autres variables... a voir
        super(DeepQNetwork, self).__init__() #constructs base class
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 64)
        self.output_layer = nn.Linear(64, output_dim)
        self.loss = nn.MSELoss() # mean squared error loss

    def forward(self, state):
        x = F.relu(self.fc1(state)) # on active ReLU
        x = F.relu(self.fc2(x))
        return self.output_layer(x)



