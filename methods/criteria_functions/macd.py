import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

def calculate_macd(series, fast_period=4, slow_period=8, signal_period=3):
    """
    Calculate MACD (Moving Average Convergence Divergence) for a time series.
    
    Args:
        series (pd.Series): Time series data
        fast_period (int): Period for fast EMA
        slow_period (int): Period for slow EMA
        signal_period (int): Period for signal line EMA
        
    Returns:
        tuple: (macd_line, signal_line, histogram)
    """
    fast_ema = series.ewm(span=fast_period, adjust=False).mean()
    slow_ema = series.ewm(span=slow_period, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram

def plot_macd(ngram, series, fast_period=3, slow_period=6, signal_period=2, threshold=2.0):
    """
    Creates a MACD analysis plot for an n-gram time series with statistical thresholds.
    
    Args:
        ngram (str): N-gram name for display purposes
        series (pd.Series): Time series data for the n-gram
        fast_period (int): Number of periods for fast EMA
        slow_period (int): Number of periods for slow EMA
        signal_period (int): Number of periods for signal line
        threshold (float): Number of standard deviations for histogram significance
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    # Calculate MACD
    macd_line, signal_line, histogram = calculate_macd(
        series, 
        fast_period=fast_period, 
        slow_period=slow_period, 
        signal_period=signal_period
    )
    
    # Calculate mean and standard deviation of histogram
    hist_mean = histogram.mean()
    hist_std = histogram.std()
    
    # Calculate upper and lower thresholds (mean ± threshold*std)
    upper_threshold = hist_mean + (threshold * hist_std)
    lower_threshold = hist_mean - (threshold * hist_std)
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, 
        cols=1,
        subplot_titles=("MACD and Signal Line", "MACD Histogram"),
        vertical_spacing=0.25,
        row_heights=[0.5, 0.5]
    )
    
    # Add MACD and signal lines to top subplot
    fig.add_trace(
        go.Scatter(
            x=macd_line.index,
            y=macd_line.values,
            mode="lines",
            name="MACD Line",
            line=dict(color="blue")
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=signal_line.index,
            y=signal_line.values,
            mode="lines",
            name="Signal Line",
            line=dict(color="red")
        ),
        row=1, col=1
    )
    
    # Add horizontal line at zero for MACD
    fig.add_hline(
        y=0, 
        line_width=1, 
        line_dash="dash", 
        line_color="gray",
        row=1, col=1
    )
    
    # Add histogram to bottom subplot with statistical threshold-based coloring
    colors = ['red' if val < lower_threshold or val > upper_threshold else 'gray' for val in histogram.values]
    
    # Make positive significant values green
    for i, val in enumerate(histogram.values):
        if val > upper_threshold:
            colors[i] = 'green'
    
    fig.add_trace(
        go.Bar(
            x=histogram.index,
            y=histogram.values,
            marker_color=colors,
            name="Histogram"
        ),
        row=2, col=1
    )
    
    # Add threshold lines for histogram
    fig.add_hline(
        y=upper_threshold, 
        line_width=1, 
        line_dash="dash", 
        line_color="green",
        annotation_text=f"+{threshold:.1f}σ",
        annotation_position="top right",
        row=2, col=1
    )
    
    fig.add_hline(
        y=lower_threshold, 
        line_width=1, 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"-{threshold:.1f}σ",
        annotation_position="bottom right",
        row=2, col=1
    )
    
    # Add horizontal line at zero for histogram
    fig.add_hline(
        y=0, 
        line_width=1, 
        line_dash="dash", 
        line_color="gray",
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        title=f"MACD Analysis for '{ngram}'",
        height=600,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified"
    )
    
    # Update axis titles
    fig.update_yaxes(title_text="Normalized Frequency", row=1, col=1)
    fig.update_yaxes(title_text="Normalized Frequency", row=2, col=1)
    
    # Show x-axis labels
    for i in range(1, 3):
        fig.update_xaxes(
            tickmode="array",
            tickvals=list(series.index),
            tickangle=270,
            row=i, col=1
        )
    
    # Only show x-axis title on bottom subplot
    fig.update_xaxes(title_text="Quarter", row=2, col=1)
    
    return fig