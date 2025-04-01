from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

import numpy
import pandas

from bacflow.modeling import calculate_bac_for_model
from bacflow.schemas import SimulationConfig, SimulationParameters, Beverage, Food, Model, Person


# Mapping of food categories to absorption halflife in seconds (6, 9, 12, 15, 18 minutes)
FOOD_HALFLIFE_MAP = {
    "snack": 6 * 60,
    "light": 9 * 60,
    "moderate": 12 * 60,
    "full": 15 * 60,
    "heavy": 18 * 60,
}


def compute_halflife_vector(
    t_sec: numpy.ndarray, food_intakes: list[Food], default_halflife: float
) -> numpy.ndarray:
    """
    Given a vector of time stamps (in seconds), compute an effective absorption halflife for each time point.
    For each t in t_sec, we use the most recent food intake (if any) to determine the halflife.
    If no food intake is available for a given t, default_halflife is used.
    """
    if not food_intakes:
        return numpy.full(t_sec.shape, default_halflife)
    # Sort food_intakes by time
    sorted_food = sorted(food_intakes, key=lambda f: f.consumed)
    food_times = numpy.array([f.consumed.timestamp() for f in sorted_food])
    food_values = numpy.array(
        [FOOD_HALFLIFE_MAP.get(f.category.lower(), default_halflife) for f in sorted_food]
    )
    # For each t in t_sec, find the index of the last food intake event (if any)
    indices = numpy.searchsorted(food_times, t_sec, side="right")
    # If no food intake before t, use default_halflife; else use the value from the most recent event.
    halflife_vector = numpy.where(indices > 0, food_values[indices - 1], default_halflife)
    return halflife_vector


def cumulative_absorption(
    drinks: list[Beverage],
    start_time: datetime,
    end_time: datetime,
    dt: float,  # simulation time step in seconds
    default_halflife: float,
    food_intakes: list[Food] | None = None,
    initial_alc: float = 0.0,
) -> pandas.DataFrame:
    """
    Compute a time series of cumulative alcohol absorption (in kg) from a list of drinks.
    The absorption at each time step is computed using a dynamic absorption halflife derived
    from food intake data. The effective halflife vector is computed so that it has the same
    length and sampling as the simulation time vector.

    Parameters:
      - drinks: list of Drink objects
      - start_time: simulation starting datetime
      - end_time: simulation ending datetime
      - dt: simulation time step in seconds
      - default_halflife: default halflife (in seconds) when no food data is present (e.g. 12 min → 720 sec)
      - food_intakes: list of Food intake objects
      - initial_alc: active absorbed alcohol (in kg) at start_time

    Returns a DataFrame with columns 'time' and 'kg_absorbed'.
    """
    t_sec = numpy.arange(start_time.timestamp(), end_time.timestamp(), dt)
    halflife_vector = compute_halflife_vector(t_sec, food_intakes, default_halflife)
    ln2 = numpy.log(2)
    absorption_mat = numpy.zeros((len(drinks), len(t_sec)))

    for i, drink in enumerate(drinks):
        drink_start = drink.consumed.timestamp()
        # Compute time deltas for all simulation points
        time_deltas = t_sec - drink_start
        # For t < drink_start, absorption is 0
        positive_deltas = numpy.maximum(time_deltas, 0)
        # Compute absorption using the dynamic halflife at each time step
        absorption_mat[i, :] = drink.quantity * (1 - numpy.exp(-positive_deltas * ln2 / halflife_vector))

    kg_absorbed = absorption_mat.sum(axis=0) + initial_alc
    df = pandas.DataFrame({"kg_absorbed": kg_absorbed, "time": t_sec})
    df["time"] = pandas.to_datetime(df["time"], unit="s", utc=True)
    return df


def simulate(config: SimulationConfig) -> pandas.DataFrame:
    """simulates the BAC evolution for the available configuration

    The simulation is going to:
      - compute the absorption halflife distribution for the given eating time-series;
      - compute the cumulative alcohol absorption time-series;
      - compute the BAC time-series via the Michaelis-Menten elimination kinetics;
      - aggregate the BAC time-series for the different simulation models.

    Args:
        config: The simulation configuration with dataset and parameters.

    Returns:
        A data frame containing the simulation results with timestamp, and concentration mean and standard deviation.
    """
    if not config.dataset.drinking:
        return pandas.DataFrame(columns=["timestamp", "mean", "stddev"])

    absorption = cumulative_absorption(
        config.dataset.drinking, 
        config.parameters.start,
        config.parameters.end,
        config.parameters.stepping,
        config.parameters.halflife,
        config.dataset.eating,
        config.parameters.quantity
    )
    results = {}
    with ThreadPoolExecutor() as executor:
        future_to_model = {
            executor.submit(calculate_bac_for_model, config.dataset.person, absorption, model, config.parameters.stepping): model
            for model in config.parameters.modeling
        }
        for future in as_completed(future_to_model):
            model = future_to_model[future]
            results[model] = future.result()
    return results


def alerting(
    simulation: pandas.DataFrame, thresholding: list[float]
) -> dict[float, datetime]:
    """detects alerting for the given simulation and parameters.

    The alerting convers the following two moments:
      - safe driving time: The time BAC will be under the DUI threshold for good.
      - sobriety: The time BAC will be null for good.
    """
    ...


def aggregate_simulation_results(
    sim_results: dict[Model, pandas.DataFrame],
) -> pandas.DataFrame:
    """
    Aggregate simulation results from different models into a single timeseries with mean and variance.
    Assumes all simulation DataFrames have the same time sampling and include a 'bac' column.

    Returns a DataFrame with columns: 'time', 'mean_bac', and 'var_bac'.
    """
    df_list = []
    for idx, (_, df) in enumerate(sim_results.items()):
        df_model = df[["time", "bac"]].copy()
        df_model = df_model.set_index("time")
        df_model = df_model.rename(columns={"bac": f"bac_{idx}"})
        df_list.append(df_model)
    all_bac = pandas.concat(df_list, axis=1)
    mean_bac = all_bac.mean(axis=1)
    std_bac = all_bac.std(axis=1)
    aggregated = pandas.DataFrame({"timestamp": all_bac.index, "mean": mean_bac, "stddev": std_bac})
    return aggregated.reset_index(drop=True)


def identify_threshold_times(
    aggregated_ts: pandas.DataFrame, driving_limit: float, tolerance: float = 1e-3
) -> tuple[pandas.Timestamp | None, pandas.Timestamp | None]:
    """
    Given an aggregated BAC timeseries (with 'mean_bac'), determine:
      - drive_safe_time: The first time (of the final continuous segment) when BAC falls below the driving_limit.
      - sober_time: The first time when BAC is effectively zero (within a tolerance) and remains at zero.

    Returns a tuple (drive_safe_time, sober_time) or (None, None) if not found.
    """
    times = aggregated_ts["time"]
    mean_bac = aggregated_ts["mean_bac"]

    drive_safe_time = None
    sober_time = None

    # Identify the final contiguous segment where BAC is below driving_limit.
    below_thresh = mean_bac < driving_limit
    segments = (below_thresh != below_thresh.shift()).cumsum()
    valid_segments = aggregated_ts[below_thresh].groupby(segments)
    if valid_segments.ngroups:
        # Use the last segment (i.e. the final time BAC is below limit)
        last_seg_indices = aggregated_ts.index[segments == segments.iloc[-1]]
        drive_safe_time = aggregated_ts.loc[last_seg_indices[0], "time"]

    # Similarly, for sober time use a tolerance (BAC effectively zero)
    sober_bool = mean_bac <= tolerance
    segments_sober = (sober_bool != sober_bool.shift()).cumsum()
    valid_sober = aggregated_ts[sober_bool].groupby(segments_sober)
    if valid_sober.ngroups:
        last_sober_indices = aggregated_ts.index[segments_sober == segments_sober.iloc[-1]]
        sober_time = aggregated_ts.loc[last_sober_indices[0], "time"]

    return drive_safe_time, sober_time
