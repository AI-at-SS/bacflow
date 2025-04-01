import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from typing import Dict

from bacflow.schemas import Threshold


def plot_simulation(simulation_df: pd.DataFrame, thresholds: Dict[Threshold, datetime]) -> go.Figure:
    """
    Plot the simulation result with confidence bands and vertical threshold lines.
    
    Args:
        simulation_df: DataFrame with columns 'timestamp', 'mean', 'stddev' where BAC values are in fraction form
        thresholds: Dictionary mapping Threshold objects to datetime objects
    
    Returns:
        A Plotly figure showing the BAC simulation with thresholds
    """
    fig = go.Figure()
    
    # Mean BAC line (convert from fraction to percentage)
    fig.add_trace(
        go.Scatter(
            x=simulation_df["timestamp"],
            y=simulation_df["mean"] * 100,
            mode="lines",
            name="Mean BAC (%)",
        )
    )
    
    # Confidence band: mean ± standard deviation
    upper = (simulation_df["mean"] + simulation_df["stddev"]) * 100
    lower = (simulation_df["mean"] - simulation_df["stddev"]) * 100
    
    fig.add_trace(
        go.Scatter(
            x=simulation_df["timestamp"],
            y=upper,
            mode="lines",
            line={"width": 0},
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=simulation_df["timestamp"],
            y=lower,
            mode="lines",
            fill="tonexty",
            line={"width": 0},
            fillcolor="rgba(0,100,80,0.2)",
            name="Confidence Band",
        )
    )
    
    # Add vertical threshold lines
    colorscale = px.colors.qualitative.Plotly  # Default Plotly color sequence
    
    # Get the y-axis range to ensure lines span the full height
    y_min = 0  # Start from zero
    y_max = upper.max() * 1.1  # Add 10% buffer above the maximum value
    
    # Vertical lines at threshold timestamps
    for i, (threshold, threshold_time) in enumerate(thresholds.items()):
        color = colorscale[i % len(colorscale)]
        if threshold_time >= min(simulation_df["timestamp"]) and threshold_time <= max(simulation_df["timestamp"]):
            # Use a scatter trace to create a vertical line spanning the full height
            fig.add_trace(
                go.Scatter(
                    x=[threshold_time, threshold_time],  # Same x value creates vertical line
                    y=[y_min, y_max],  # From bottom to top of the chart
                    mode="lines",
                    line={"dash": "dash", "color": color},
                    name=f"{threshold.description}: {threshold.value * 100:.2f}%",
                )
            )
            # Add annotation near the top
            fig.add_annotation(
                x=threshold_time,
                y=y_max,
                text=f"{threshold.description}",
                showarrow=False,
                yshift=10
            )
    
    # Update y-axis range to ensure vertical lines are fully visible
    fig.update_layout(
        title="BAC Simulation",
        xaxis_title="Time",
        yaxis_title="BAC (%)",
        template="plotly_white",
        yaxis=dict(range=[y_min, y_max])
    )
    
    return fig
