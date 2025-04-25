import matplotlib.pyplot as plt


def plot_graph(x, y, save_path, title="Title", x_lab="x", y_lab="y"):
    plt.figure(figsize=(12, 6))
    plt.plot(x, y)
    plt.xlabel(x_lab)
    plt.ylabel(y_lab)
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', transparent=True)