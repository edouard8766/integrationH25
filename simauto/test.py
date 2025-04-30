import os.path
from simauto.Tools import plot_graph
import gymnasium as gym
import simauto.register_env  # must import to register the env
import torch as T
import numpy as np
from dqn import *
from simauto.agent import DQNAgent, state_tensor


device = T.device("cuda" if T.cuda.is_available() else "cpu")
env = gym.make("Intersection-v0", render_mode=None, step_length=6.0)
input_dim = 4 + 4 #+ 6
output_dim = 6
agent = DQNAgent(input_dim, output_dim)

#Hyperparameters
BATCH_SIZE = 32
GAMMA = 0.97
EPSILON_DECAY = 0.995
MIN_EPSILON = 0.005
TARGET_UPDATE_FREQ = 1000
episode_rewards = []
episode_epsilons = []
episode_mean_wait = []
episode_emissions = []
total_steps = 0
n_episode = 1500
for episode in range(n_episode):
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

        # Train from buffer
        if len(agent.buffer.buffer) > BATCH_SIZE:
            states, actions, rewards, next_states, dones = agent.buffer.sample(BATCH_SIZE)
            states = T.FloatTensor(states).to(device)
            next_states = T.FloatTensor(next_states).to(device)

            # DQN Loss Calculation
            q_values = agent.q_net(states)
            next_q_values = agent.target_net(next_states).max(1)[0].detach()
            rewards_tensor = T.FloatTensor(rewards).to(device)
            dones_tensor = T.FloatTensor(dones)
            targets = rewards_tensor + (1 - dones_tensor) * agent.gamma * next_q_values
            actions_tensor = T.LongTensor(actions).to(device)

            loss = agent.q_net.loss(q_values.gather(1, actions_tensor.unsqueeze(1)), targets.unsqueeze(1))
            agent.optimizer.zero_grad()
            loss.backward()
            agent.optimizer.step()

            # Update target network
            total_steps += 1
            if total_steps % TARGET_UPDATE_FREQ == 0:
                agent.update_target_network()


    #Calculate mean wait for the episode
    sum = 0
    mean_waits = env.unwrapped.mean_waits
    for w in mean_waits:
        sum += w
    mean_wait = sum/len(mean_waits)

    episode_rewards.append(total_reward)
    episode_epsilons.append(agent.epsilon)
    episode_mean_wait.append(mean_wait)
    episode_emissions.append(env.unwrapped.sim.emissions)
    print(f"Episode {episode}, Reward: {total_reward:.2f}, Epsilon: {agent.epsilon:.2f}, Mean wait: {mean_wait:.2f}, Emissions: {env.unwrapped.sim.emissions:.2f}")
    agent.epsilon = max(MIN_EPSILON, agent.epsilon * EPSILON_DECAY)

path = os.path.join("saved_models", "model0.txt")
path = "model0.txt"
agent.save(path)

episodes = [[i] for i in range(n_episode)]
plot_graph(episodes, episode_rewards, "reward-episode.png", "Récompense selon l'épisode", "Épisode", "Récompense")
plot_graph(episodes, episode_epsilons, "epsilon-episode.png", "Valeur d'epsilon selon l'épisode", "Épisode", "ε")
plot_graph(episodes, episode_mean_wait, "mean_wait-episode.png", "Temps d'attente moyen à l'intersection selon l'épisode", "Épisode", "Temps d'attente moyen")
plot_graph(episodes, episode_emissions, "emissions-episode.png", "Émissions de CO2 selon l'épisode", "Épisode", "Émissions de CO2 (L)")
env.close()
