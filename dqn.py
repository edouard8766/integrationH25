import numpy as np
import torch as T
import torch.nn as nn# torch neural network
import torch.nn.functional as F
import torch.optim as optim
import random

from main import state_tensor

input_dim = 4 + 4 + 6# dans le dico pressure(4), nearest(4), lights(6)
output_dim = 0

class DeepQNetwork(nn.Module):

    def __init__(self, input_dim, output_dim): # maybe faut mettre d'autres variables... a voir
        super(DeepQNetwork, self).__init__() #constructs base class

        self.fc1 = nn.Sequential( #features 1, je le mets sequential pour que ca soit plus propre
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128,64),#hidden layer
            nn.ReLU()
        )

        self.output_layer = nn.Linear(64, output_dim)

    def forward(self, state):
        print(state.shape)
        features = self.fc1(state)
        return self.output_layer(features)



