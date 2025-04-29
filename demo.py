import gymnasium as gym
import simauto.register_env
from agent import DQNAgent
from simauto.sim import TrafficSignalPhase
import sys

env = gym.make("Intersection-v0", render_mode="human", step_length=0.25)

class PhaseCycle:
    cycle: list[tuple[TrafficSignalPhase, float]]
    _current: int

    def __init__(self, cycle: list[tuple[TrafficSignalPhase, float]]):
        self.cycle = cycle
        self._current = 0

    @property
    def current_phase(self):
        return self.cycle[self._current][0]

    @property
    def current_phase_duration(self):
        return self.cycle[self._current][1]

    def next(self):
        self._current = (self._current + 1) % len(self.cycle)
        return self.current_phase

def demo_cycle(cycle: PhaseCycle):
    done = False
    obs, info = env.reset()
    last_phase_instant = 0
    sim_elapsed = info["elapsed_time"]
    while not done:
        time_since_last_phase = sim_elapsed - last_phase_instant
        if time_since_last_phase >= cycle.current_phase_duration:
            cycle.next()
            last_phase_instant = sim_elapsed

        env.render()

        obs, reward, terminated, truncated, info = env.step(cycle.current_phase.value)
        sim_elapsed = info["elapsed_time"]

        done = truncated

def demo_agent(agent: DQNAgent):
    done = False
    step = 0
    action = 0
    obs, _ = env.reset()
    while not done:
        if step % 40 == 0:
            action = agent.act(env.unwrapped.get_obs_tensor())
        obs, reward, terminated, truncated, _ = env.step(action)
        env.render()
 
        done = truncated
        step += 1

if __name__ == "__main__":
    args = sys.argv
    is_cycles_demo = len(args) > 1 and args[1] == "cycles"

    if is_cycles_demo:
        cycle = PhaseCycle([
            (TrafficSignalPhase.EastWestPermitted, 30.),
            (TrafficSignalPhase.NorthSouthPermitted, 30.),
        ])
        demo_cycle(cycle)
    else:
        agent = DQNAgent(env)
        agent.load("saved_models/model0.txt")
        demo_agent(agent)

    env.close()
