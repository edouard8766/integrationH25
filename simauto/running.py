import gymnasium as gym
import torch as T
import numpy as  np
import random
from car import Car, CarIntention
from intersection import IntersectionEnv
from dqn import *

#init env
steps_per_second = 1 #steps/sec
env = IntersectionEnv(steps_per_second)
initial_epsilon = 0.9 #90%
final_epsilon = 0.05 # final
total_timesteps = 10000 # total training steps
timestep = 0


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

model = DeepQNetwork(input_dim=input_dim, output_dim=6)
optimizer = optim.Adam(model.parameters(), lr=0.001)

while running:

    if env.frame_counter % (env.fps / steps_per_second) == 0:
        #seulement quand pas jaune, jaune = ralentit svp
        if not env.yellow_light_on:

            progress = timestep / total_timesteps
            epsilon = (final_epsilon - initial_epsilon) * max(progress, 0.0) + initial_epsilon
            #on prep pour avoir le dqn
            state_tensor = T.tensor(obs, dtype=T.float32).unsqueeze(0) # on le met soit ici soit apres le else, jsp trop
            #on convert l'observation a un tensor(matrice)
            #unsqueeze(0) ajoute une "batch dimension" qui est requise(selon la documentation entk j'ai compris ca)
            for i in range(1, 9):
                for car in env.lanes[i]:
                    crossed_line = env.check_intersection_cross(car)
                    #distance_moved = car.step(stop_distance=None, delta_time=steps_per_second)

            if random.uniform(0, 1) < epsilon:
                action = env.action_space.sample() #action random jsp quoi mettre pour l'instant
                #print("selected random action :", action) #pour debug

            else:
                with T.no_grad(): #pas de calcul de gradient, sinon ca interfere
                    #q_values = model(state_tensor) # les q_values
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

            #------------
            #Si on veut mettre un replay buffer, faut le mettre ici, jsp comment mais faudrait store le (state, action, reward, next_state)
            #------------

            timestep += 1

            obs = next_obs # current -> next


            if terminated or truncated:
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