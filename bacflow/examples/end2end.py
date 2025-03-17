from datetime import datetime, timedelta, timezone

from bacflow.schemas import Drink, Person, Model, Sex
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
drinks = [drink1]

# Create a sample person
person = Person(age=30, height=1.75, weight=70, sex=Sex.M)

# Simulate using a selected model (e.g., Seidl)
sim_models = [Model.Seidl]
sim_results = simulate(drinks, person, start_time, end_time, dt, default_halflife, initial_alc, sim_models)

# Aggregate results if multiple models are simulated
aggregated = aggregate_simulation_results(sim_results)

# Identify key threshold times (e.g., driving limit of 0.02 g/dL)
driving_limit = 0.02
drive_safe_time, sober_time = identify_threshold_times(aggregated, driving_limit)

print("Drive Safe Time:", drive_safe_time)
print("Sober Time:", sober_time)

fig = plot_simulation(aggregated, driving_limit)
fig.show()
