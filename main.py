import gymnasium as gym
import torch as T
import numpy as  np
import random
import os
import csv
from simauto.intersection import IntersectionEnv

from dqn import *

#init env
steps_per_second = 1 #steps/sec
env = IntersectionEnv(steps_per_second)
initial_epsilon = 0.9 #90%
final_epsilon = 0.05 # final
total_timesteps = 10000 # total training steps
timestep = 0

log_file = "logs.csv"


#reset and start
obs, info = env.reset()
#on assume que obs est deja dans le bon format pis on le met dans un array flat
obs = np.stack([
    obs["pressure"],
    obs["nearest"],
    #obs["lights"]
], axis=0).astype(np.float32)

#obs = np.array([obs["pressure"], obs["nearest"], obs["lights"]], dtype=np.float32)
running = True

device = T.device("cuda:0" if T.cuda.is_available() else "cpu") # va chercher le gpu/cpu pis deplace le model dessus
model = DeepQNetwork(input_dim=input_dim, output_dim=6).to(device)
state_tensor = state_tensor.to(device)#pour send les input au device aussi
optimizer = optim.Adam(model.parameters(), lr=0.001)

if not os.path.exists(log_file):
    with open(log_file, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestep", "epsilon", "Avg Wait Time", "Cars Passed", "Total Reward", "Bad Rewards", "Emissions"])

def log_data(timestep, epsilon, avg_wait_time, cars_passed, total_reward, bad_rewards, emissions):
    with open(log_file, mode="a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([timestep, epsilon, avg_wait_time, cars_passed, total_reward, bad_rewards, emissions])

while running:

    if env.frame_counter % (env.fps / steps_per_second) == 0:
        #seulement quand pas jaune, jaune = ralentit svp
        if not env.yellow_light_on:

            avg_wait_time = 0.0
            cars_passed = 0.0
            total_reward = 0.0
            bad_rewards = 0.0
            emissions = 0.0

            progress = timestep / total_timesteps
            epsilon = (final_epsilon - initial_epsilon) * max(progress, 0.0) + initial_epsilon
            #on prep pour avoir le dqn
            state_tensor = T.tensor(obs, dtype=T.float32).unsqueeze(0) # on le met soit ici soit apres le else, jsp trop
            #on convert l'observation a un tensor(matrice)
            #unsqueeze(0) ajoute une "batch dimension" qui est requise(selon la documentation entk j'ai compris ca)


            if random.uniform(0, 1) < epsilon:
                action = env.action_space.sample() #action random jsp quoi mettre pour l'instant
                #print("selected random action :", action) #pour debug

            else:
                with T.no_grad(): #pas de calcul de gradient, sinon ca interfere
                    q_values = model(state_tensor) # les q_values
                    action = T.argmax(q_values).item() #choose avec la plus grande q_value
                    #print("Exploit : selected best action: ", action) # debug


            #chosen action sent to env.step()
            next_obs, reward, terminated, truncated, info = env.step(action)
            #convert next_obs to array
            next_obs = np.stack([
                next_obs["pressure"],
                next_obs["nearest"],
                # obs["lights"]
            ], axis=0).astype(np.float32)
            #next_obs = np.array(next_obs, dtype=np.float32)

            total_reward += reward
            if reward < 0:
                bad_rewards += reward # ou bad rewards += 1

            #------------
            #Si on veut mettre un replay buffer, faut le mettre ici, jsp comment mais faudrait store le (state, action, reward, next_state)
            #------------

            timestep += 1

            #avg_wait_time = info.get("avg_wait_time", 0)
            #emissions = info.get("emissions",0)

            obs = next_obs # current -> next
            if timestep % 10 == 0:
                log_data(timestep, epsilon, avg_wait_time, cars_passed, total_reward, bad_rewards, emissions)


            if timestep >= total_timesteps or terminated or truncated:
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