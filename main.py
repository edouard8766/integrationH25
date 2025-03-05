import numpy as np
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import random

#
class DeepQNetwork(nn.Module):
    def __init__(self): # maybe faut mettre d'autres variables... a voir
        super(DeepQNetwork, self).__init__() #constructs base classs