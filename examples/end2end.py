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
