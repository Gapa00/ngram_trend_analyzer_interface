import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

def calculate_pct(series, periods):
    return series.pct_change(periods=periods)

def plot_percent_change(ngram, series, periods=4, threshold=2.0):
    """
    Creates a plot showing the percent change with threshold lines at specified standard deviations.
    
    Args:
        ngram (str): N-gram to analyze
        series (pd.Series): Time series data for the n-gram
        periods (int): Number of periods to calculate change over
        threshold (float): Number of standard deviations for threshold lines
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    # Calculate percent change
    pct_change = calculate_pct(series, periods)
    
    # Calculate mean and standard deviation for threshold lines
    pct_mean = pct_change.mean()
    pct_std = pct_change.std()
    
    # Calculate upper and lower threshold values
    upper_threshold = pct_mean + (threshold * pct_std)
    lower_threshold = pct_mean - (threshold * pct_std)
    
    # Create figure
    fig = go.Figure()
    
    # Add percent change line
    fig.add_trace(
        go.Scatter(
            x=pct_change.index,
            y=pct_change.values,
            mode="lines+markers",
            name="Percent Change",
            line=dict(color="red")
        )
    )

    # Add horizontal lines at threshold standard deviations
    fig.add_hline(
        y=upper_threshold, 
        line_width=1, 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"+{threshold:.1f}σ",
        annotation_position="top right"
    )
    
    fig.add_hline(
        y=lower_threshold, 
        line_width=1, 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"-{threshold:.1f}σ",
        annotation_position="bottom right"
    )
    
    # Update layout
    fig.update_layout(
        title=f"Percent Change for '{ngram}' (Period: {periods})",
        xaxis_title="Quarter",
        yaxis_title="Percent Change",
        height=400,
        showlegend=False,
        template="plotly_white"
    )
    
    # Show x-axis labels
    fig.update_xaxes(
        tickmode="array",
        tickvals=list(pct_change.index),
        tickangle=270
    )
    
    return fig