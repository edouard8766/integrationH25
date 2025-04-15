from simauto.intersection import IntersectionEnv

def make_env(step_length=1.0):
    return IntersectionEnv(step_length=step_length)
