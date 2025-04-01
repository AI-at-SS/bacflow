import os

import yaml

from bacflow.plotting import plot_simulation
from bacflow.schemas import SimulationConfig
from bacflow.simulation import alerting, simulate


absfile = os.path.join(os.path.dirname(__file__), "config.yaml")

config = SimulationConfig.from_file(absfile)

simulation = simulate(config)

DUI, sobriety = alerting(simulation, config.parameters)

print("safe driving time:", DUI)
print("sobriety time:", sobriety)

figure = plot_simulation(simulation, config.parameters)
figure.show()
