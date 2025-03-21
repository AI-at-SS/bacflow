import os

import yaml

from bacflow.plotting import plot_simulation
from bacflow.schemas import SimulationConfig
from bacflow.simulation import alerting, simulate


absfile = os.path.join(os.path.dirname(__file__), "end2end.yaml")

with open(absfile, "r") as f:
    mapping = yaml.safe_load(f)

config = SimulationConfig.from_mapping(mapping)

simulation = simulate(config)

DUI, sobriety = alerting(simulation, config.parameters)

print("safe driving time:", DUI)
print("sobriety time:", sobriety)

figure = plot_simulation(simulation, config.parameters)
figure.show()
