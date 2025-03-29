<div align="center">

# BACflow

<img src="static/BACflow.png" width="256" height="256"/>

simulation framework for blood alcohol content (BAC) estimation.

</div>

## 🌟 overview

BACflow is the minute-scale SOTA simulation framework for blood alcohol content (BAC) estimation with support for all classical modelling methods derived from E. Widmark's research[^1], for Michaelis-Menten kinetics, and for dynamic modeling of food intake.

The framework is advancing the SOTA in all three phases of alcohol interaction within the human body: absorption, distribution, and elimination.

## ✨ features

- **dynamic alcohol absorption**: adjusts alcohol absorption halflife based on food intake data.
- **flexible simulation**: supports user-defined simulation bounds, initial conditions, and time-step granularity.
- **multiple models**: includes Seidl, Widmark, Forrest, Watson, Ulrich, and an average model.
- **threshold identification**: detects key milestones such as when BAC drops below driving limits or reaches zero.
- **efficient computations**: leverages NumPy and Pandas for high-performance, vectorized operations.
- **modular design**: separates core BAC computations from user interfaces.

## 📦 installation

Install BACflow using pip (Python 3.8+):

```bash
pip install bacflow
```

## 💻 usage

Below is a simple example to simulate BAC from a list of drinks using a single model:

```python
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
```

To run the example, you shall execute:

```shell
uv run examples/end2end.py
```

and see what a complete [simulation config](examples/end2end.yaml) is made of.

## 📚 API documentation

API documentation will be available in future releases.

## 🤝 contributing

Contributions are welcome! Fork the repository, create a branch for your feature or bug fix, write tests to cover your changes, and submit a pull request.

```bash
git clone https://github.com/yourusername/bacflow.git
cd bacflow
uv sync --all-extras
```

## 🔗 license

See the [LICENSE](LICENSE) file for more details.

## 🙌 acknowledgements

Inspired by the foundational work of Widmark and further studies on alcohol metabolism. Special thanks to all contributors and the open-source community.

- [BAC-simulator](https://github.com/bcyran/bac-simulator)
- [drinkR - estimate your BAC](https://www.sumsar.net/blog/2014/07/estimate-your-bac-using-drinkr/)
- [drinkR - repository](https://github.com/rasmusab/drinkr)
- [get-BAC](https://getbacsoftware.org/)
- [Michaelis–Menten kinetics](https://en.wikipedia.org/wiki/Michaelis%E2%80%93Menten_kinetics)

[^1]: [D. Posey and A. Mozayani, The Estimation of Blood Alcohol Concentration: Widmark Revisited, 2007](https://doi.org/10.1385/fsmp:3:1:33)
