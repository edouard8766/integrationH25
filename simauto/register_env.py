from gymnasium.envs.registration import register
from simauto.intersection import IntersectionEnv

def make_env(**kwargs):
    return IntersectionEnv(**kwargs)

register(
    id="Intersection-v0",
    entry_point="simauto.register_env:make_env",
)
