# Integration25
**A Python tool using deep learning to optimally control traffic lights.**

**Status:** Completed CEGEP Final Project


Integration25 is a final project for a CEGEP course where a team of five students explored deep learning and reinforcement learning techniques (Deep Q-Learning with PyTorch) to develop an intelligent agent capable of managing traffic lights efficiently. The goal was both to research practical applications of deep learning and to build a working simulation.
## Table of Contents

- [About](#about)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
## About

Integration25 is a Python project designed to optimize traffic flow at a 4-way intersection with two lanes per road. The goal was to reduce vehicle wait times and experiment with AI techniques for urban planning.  

The system simulates traffic where the agent has access to the position and velocity of all cars near the intersection, similar to what a real-world camera could observe. Using Deep Q-Learning implemented in PyTorch, the agent makes decisions on traffic light states based on the observed traffic conditions.  

The project also includes a visual simulation using Pygame, allowing observation of the agent's behavior in real time. Results showed a significant decrease in vehicle wait times, demonstrating the effectiveness of reinforcement learning for traffic management.
## Getting Started

These instructions will help you set up and run Integration25 on your local machine.

### Prerequisites

- [Python 3.13](https://www.python.org/downloads/release/python-3130/)
- [PyTorch](https://pytorch.org/)
- [Pygame](https://www.pygame.org/)
- [Matplotlib](https://matplotlib.org/)
- [NumPy](https://numpy.org/)
- [Gymnasium](https://www.gymnasium.ai/)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/edouard8766/integrationH25.git
cd integrationH25
```

2. Install dependencies manually (listed in pyproject.toml)

### Configuration
Default settings work out of the box. You can modify parameters in the configuration files if needed.
### Running the Project
#### 1. Train the agent
```bash
python train.py
```
#### 2. Run the demo / simulation:
``` bash
python demo.py
```
Note: You should run train.py before running demo.py to ensure the agent has a trained model.
## Usage

A typical workflow for using Integration25 is:

1. Train the agent using `train.py`.
2. Run the simulation demo using `demo.py`.
3. Analyze the results (plots and statistics).
4. Adjust parameters if needed.
5. Retrain to improve performance.

### Simulation Visualization

When running the demo, you will see a graphical simulation of a 4-way intersection:

- Cars move along the lanes.
- Traffic lights are represented by colored bars above the corresponding lanes.
- Real-time plots are generated for metrics such as:
  - Epsilon decay
  - CO₂ emissions
  - Average wait time

### Example Screenshot

![Simulation Screenshot](https://github.com/edouard8766/integrationH25/blob/main/Demo-visualisation.png)
## Project Structure

Below is an overview of the main folders and files in the repository:

### Folder / File Layout
```
integrationH25/
│
├── .idea/ ← IDE configuration files
├── graphs/ ← Stored plots/visualisations (e.g., epsilon decay, CO₂, wait time)
├── saved_models/ ← Trained model checkpoints
├── simauto/ ← Simulation and environment code (4‑way intersection)
│
├── agent.py ← Defines the RL agent class, decision logic
├── dqn.py ← Deep Q‑Learning implementation (network, memory, update)
├── demo.py ← Runs the simulation demo with a trained agent
├── main.py ← Entry point / high‑level script to set up environment + run train/demo
├── train.py ← Script to train the agent from scratch
├── util.py ← Utility functions (logging, metrics, plotting, environment helpers)
├── info.md ← Project info, setup notes or other documentation
├── pyproject.toml ← Dependency & build configuration
├── README.md ← This file
└── .gitignore ← Specifies files/folders Git should ignore
```
### Explanation of Key Components

- **`simauto/`**  
  This directory contains the environment simulation of the 4‑way intersection (2 lanes each direction), car generation, lane logic, traffic light representation and visualization via Pygame.

- **`agent.py`**  
  Implements the agent that observes the environment (positions & velocities of cars) and decides traffic‑light states. Encapsulates policy logic and interfaces with the DQN.

- **`dqn.py`**  
  Contains the implementation of the Deep Q‑Learning algorithm: neural network architecture, replay buffer, update logic, epsilon‑greedy scheduling, loss calculation, etc.

- **`train.py`**  
  A script that sets up the environment and agent, runs episodes, tracks metrics (e.g., wait time, CO₂ emissions, epsilon decay), and saves the trained model to `saved_models/`.

- **`demo.py`**  
  Runs the simulation in real time using a trained model. Shows Pygame visualization of the intersection, colored‑bar traffic lights, and updates the user with metric plots (epsilon decay, CO₂, wait time).

- **`main.py`**  
  High‑level script that may combine set‑up and invocation logic (for example choosing mode train vs demo, parsing arguments or config).

- **`util.py`**  
  Utility functions for common tasks: logging, plotting graphs, loading/saving models, environment wrappers, etc.

- **`graphs/` & `saved_models/`**  
  - `graphs/` stores metrics plots after training (visualisation of epsilon‑decay, CO₂ emissions, wait times).  
  - `saved_models/` stores checkpoint files of the trained agent (for reuse during demo or further training).

- **`info.md`**  
  Provides additional documentation or notes about the project (e.g., dataset, configuration details, environment setup).

- **`pyproject.toml`**  
  Lists project dependencies (Python version, PyTorch, Pygame, NumPy, Gymnasium, Matplotlib) and build settings.

---

This structure should help new contributors or users quickly understand where to look for code, how things are organised, and what each part does.
## Features

- Train a reinforcement learning (RL) agent using Deep Q-Learning.
- Simulate a 4-way intersection with two lanes per road.
- Display real-time traffic and visual plots using Pygame.
- Track key metrics including vehicle wait time and CO₂ emissions.

> No future updates or features are currently planned.
## Contributing

This project was developed as a final CEGEP course project by a team of five students.  
The project is now complete, and no external contributions or modifications are accepted.
## License

The Integration25 project is owned by the five students who developed it.  

It is free to use for any **non-commercial** purposes. If you use this project, please acknowledge the authors’ work.  

> No formal open-source license is applied. All rights are retained by the original team.
## Acknowledgments

This project was made possible thanks to the contributions of the following team members:  
**Edouard, Isaac, Hugo, Louis-Charles, Simon**

We would also like to acknowledge the following libraries and tools that were essential for the project:  

- [PyTorch](https://pytorch.org/) – for implementing Deep Q-Learning  
- [Pygame](https://www.pygame.org/) – for simulation visualization  
- [Matplotlib](https://matplotlib.org/) – for plotting metrics  
- [NumPy](https://numpy.org/) – for numerical computations  
- [Gymnasium](https://www.gymnasium.ai/) – for simulation environment setup
