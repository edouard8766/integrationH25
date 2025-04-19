import matplotlib.pyplot as plt
import pickle
from sim import IntersectionSimulation

def load_sim_data(filename=""):
    with open(filename, "rb") as f:
        return pickle.load(f)

def plot_metrics(metrics):
    plt.figure(figsize=(18, 12))

    #wait time
    plt.subplot(2,2,1)
    plt.plot(metrics[''], metrics["wait_times"])
    plt.title("Average wait time over time")
    plt.xlabel("Time")
    plt.ylabel("Average wait time")


if __name__ == "__main__":
    metrics = load_sim_data()
    plot_metrics(metrics)