import gymnasium as gym
import simauto.register_env
from dqn import *
from simauto.agent import state_tensor
from simauto.Tools import plot_graph


def light_cycle(n):
    match n:
        case 0:
            return 1
        case 1:
            return 0
        case 2:
            return 2
        case 3:
            return 4
        case 4:
            return 3
        case 5:
            return 5

device = T.device("cuda" if T.cuda.is_available() else "cpu")

# Create environment and agent
env = gym.make("Intersection-v0", render_mode=None, step_length=6)
light_duration = 3
countdown = 5
n = 0

# Run one episode for demo
obs, _ = env.reset()
state = state_tensor(obs)
action = True
done = False

episode_rewards = []
episode_epsilons = []
episode_mean_wait = []
episode_emissions = []
total_steps = 0
n_episode = 1

for episode in range(n_episode):
    obs, _ = env.reset()
    state = state_tensor(obs)
    total_reward = 0
    done = False
    while not done:
        countdown -= 1
        if countdown <= 0:
            n+=1
            if n > 5:
                n = 0
            action = light_cycle(n)
            countdown = 5
        next_obs, reward, terminated, truncated, _ = env.step(action)
        total_reward += reward
        env.render()
        done = terminated or truncated
        total_reward += reward

    # Calculate mean wait for the episode
    sum = 0
    mean_waits = env.unwrapped.mean_waits
    for w in mean_waits:
        sum += w
    mean_wait = sum / len(mean_waits)
    episode_rewards.append(total_reward)
    episode_mean_wait.append(mean_wait)
    episode_emissions.append(env.unwrapped.sim.emissions)
    print(f"Episode {episode}, Reward: {total_reward:.2f}, Mean wait: {mean_wait:.2f}, Emissions: {env.unwrapped.sim.emissions:.2f}")

episodes = [[i] for i in range(n_episode)]
plot_graph(episodes, episode_rewards, "reward-episode-cycles.png", "Récompense selon l'épisode", "Épisode", "Récompense")
plot_graph(episodes, episode_mean_wait, "mean_wait-episode-cycles.png", "Temps d'attente moyen à l'intersection selon l'épisode", "Épisode", "Temps d'attente moyen")
plot_graph(episodes, episode_emissions, "emissions-episode-cycles.png", "Émissions de CO2 selon l'épisode", "Épisode", "Émissions de CO2 (L)")

env.close()
