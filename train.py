from dataclasses import dataclass
from typing import ClassVar
from agent import DQNAgent
import gymnasium as gym
import torch as T
import numpy as np
from util import save_graph
from dqn import *
import sys
import os
import time

import simauto.register_env  # must import to register the env


@dataclass
class Hyperparameters:
    batch_size: int
    discount_factor: float
    update_frequency: int
    epsilon_decay: float
    epsilon_min: float

    def default():
        return Hyperparameters(
            batch_size = 32, discount_factor = 0.97,
            epsilon_decay = 0.995, epsilon_min = 0.005,
            update_frequency = 1000
        )

@dataclass
class TrainingResult:
    agent: DQNAgent
    rewards: list[float]
    mean_waits: list[float]
    emissions: list[float]


def train(env, episodes = 200, device = "cpu", params: Hyperparameters = Hyperparameters.default()) -> TrainingResult:
    agent = DQNAgent(env, epsilon=1.)
    episode = 1
    total_steps = 0

    episode_rewards = []
    episode_mean_waits = []
    episode_emissions = []

    for episode in range(episodes):
        obs, _ = env.reset()
        done = False
        state = env.unwrapped.get_obs_tensor().to(device)
        total_reward = 0.

        while not done:
            action = agent.act(state)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            next_state = env.unwrapped.get_obs_tensor().to(device)

            agent.buffer.store(state.numpy(), action, reward, next_state.numpy(), done)
            state = next_state
            total_reward += reward

            # Train from buffer
            if len(agent.buffer.buffer) > params.batch_size:
                states, actions, rewards, next_states, dones = agent.buffer.sample(params.batch_size)
                states = T.FloatTensor(states).to(device)
                next_states = T.FloatTensor(next_states).to(device)

                q_values = agent.q_net(states)
                next_q_values = agent.target_net(next_states).max(1)[0].detach()

                rewards_tensor = T.FloatTensor(rewards).to(device)
                dones_tensor = T.FloatTensor(dones)

                targets = rewards_tensor + (1 - dones_tensor) * agent.gamma * next_q_values
                actions_tensor = T.LongTensor(actions).to(device)

                loss = agent.q_net.loss(
                    q_values.gather(1, actions_tensor.unsqueeze(1)),
                    targets.unsqueeze(1)
                )

                agent.optimizer.zero_grad()
                loss.backward()
                agent.optimizer.step()

                total_steps += 1
                if total_steps % params.update_frequency == 0:
                    agent.update_target_network()

            mean_waits = env.unwrapped.mean_waits
            mean_wait = sum(mean_waits)/len(mean_waits)
            

        episode_rewards.append(total_reward)
        episode_mean_waits.append(mean_wait)
        episode_emissions.append(env.unwrapped.sim.emissions)
        local_time = time.strftime("%H:%M:%S", time.localtime())
        print(f"[{episode + 1}] (ε={agent.epsilon:.2f}) Reward: {total_reward:.2f}, Mean wait: {mean_wait:.2f}, Emissions: {env.unwrapped.sim.emissions:.2f}, at: {local_time}")

        agent.epsilon = max(params.epsilon_min, agent.epsilon * params.epsilon_decay)
        episode += 1

    return TrainingResult(agent, episode_rewards, episode_mean_waits, episode_emissions)

if __name__ == "__main__":
    args = sys.argv
    episodes = int(args[1]) if len(args) > 1 else 200
    model_path = os.path.join("saved_models", "model0.txt")
    def graph_path(name): return os.path.join("graphs", name + ".png")
    env = gym.make("Intersection-v0", step_length=6)
    device = T.device("cuda" if T.cuda.is_available() else "cpu")

    params = Hyperparameters(
        batch_size = 32, discount_factor = 0.97,
        epsilon_decay = 0.995, epsilon_min = 0.005,
        update_frequency = 1000
    )

    print(f'''
==== Started Training Session ====
Number of episodes : {episodes}
==================================
''')
    start_time = time.time()

    result = train(env, episodes, device=device)

    runtime_duration = time.time() - start_time
    minutes = runtime_duration // 60
    seconds = runtime_duration % 60
    formated_duration = f"{minutes}m {seconds:.0f}s" if minutes > 0 else f"{seconds:.0f}s"

    print(f'''
======= Training Completed =======
Number of episodes : {episodes}
Duration           : {formated_duration}
==================================
''')

    result.agent.save(model_path)
    print(f"Model saved to '{model_path}'")

    episodes = list(range(1, episodes + 1))

    save_graph(episodes, result.rewards, graph_path("reward"), title="Rewards")
    print(f"Graph saved to '{graph_path("reward")}'")
    save_graph(episodes, result.mean_waits, graph_path("mean_waits"), title="Mean waits")
    print(f"Graph saved to '{graph_path("mean_waits")}'")
    save_graph(episodes, result.emissions, graph_path("emission"), title="Emissions")
    print(f"Graph saved to '{graph_path("emission")}'")
    
    env.close()

