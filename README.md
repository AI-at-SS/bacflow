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
from datetime import datetime, timedelta, timezone, date

from bacflow.schemas import Drink, Person, Model, Sex, FoodIntake
from bacflow.plotting import plot_simulation
from bacflow.simulation import simulate, aggregate_simulation_results, identify_threshold_times


# Define simulation parameters
start_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
end_time = start_time + timedelta(hours=2)
dt = 60  # 1-minute time step
default_halflife = 720  # default halflife in seconds (12 minutes)
initial_alc = 0.0

# Create a sample drink list
drink1 = Drink(
    name="Beer",
    vol=0.33,           # in liters
    alc_prop=0.05,      # 5% alcohol
    time=start_time + timedelta(minutes=10),
    sip_interval=1
)
drink2 = Drink(
    name="Wine",
    vol=0.15,           # in liters
    alc_prop=0.12,      # 12% alcohol
    time=start_time + timedelta(minutes=20),
    sip_interval=1
)
drinks = [drink1, drink2]

# Add a sample food intake
food_intake = FoodIntake(
    time=start_time + timedelta(minutes=15),
    category="moderate"  # using string; alternatively, FoodIntakeCategory.moderate if imported
)
food_intakes = [food_intake]

# Create a sample person
person = Person(DoB=date(1997, 5, 31), height=1.75, weight=70, sex=Sex.M)

# Simulate using a selected model (e.g., Seidl)
sim_models = [Model.Seidl]
sim_results = simulate(drinks, person, start_time, end_time, dt, default_halflife, initial_alc, sim_models, food_intakes)

# Aggregate results if multiple models are simulated
aggregated = aggregate_simulation_results(sim_results)

# Identify key threshold times (e.g., driving limit of 0.02 g/dL)
driving_limit = 0.02
drive_safe_time, sober_time = identify_threshold_times(aggregated, driving_limit)

print("Drive Safe Time:", drive_safe_time)
print("Sober Time:", sober_time)

fig = plot_simulation(aggregated, driving_limit)
fig.show()
```

To run the example, you shalle execute:

```shell
uv run examples/end2end.py
```

## 📚 api documentation
API documentation will be available in future releases.

## 🤝 contributing
Contributions are welcome! Fork the repository, create a branch for your feature or bug fix, write tests to cover your changes, and submit a pull request.

```bash
git clone https://github.com/yourusername/bacflow.git
cd bacflow
uv sync --extra contrib
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
