import os
from datetime import datetime, timedelta

import pandas

from bacflow.plotting import plot_simulation
from bacflow.schemas import Threshold


absfile = os.path.join(os.path.dirname(__file__), "dataset.csv")

simulation = pandas.read_csv(absfile)
simulation["timestamp"] = pandas.to_datetime(simulation["timestamp"])
dataframe = SimulationOutput.from_file().pandas()


# Sample usage in main
if __name__ == "__main__":
    # Load or generate sample data
    df = load_or_generate_data()
    
    # Get the start time from the data for threshold reference points
    start_time = df["timestamp"].min()
    
    # Create threshold dictionary using Threshold objects
    thresholds = {
        Threshold(description="sobriety", value=0.): start_time + timedelta(hours=6),
        Threshold(description="DUI", value=0.05): start_time + timedelta(hours=2),
    }
    
    # Generate plot
    fig = plot_simulation(df, thresholds)
    
    # Show plot
    fig.show()
    
    print("Plot generated successfully!")
