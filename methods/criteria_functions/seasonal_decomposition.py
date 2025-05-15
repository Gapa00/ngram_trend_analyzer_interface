import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from statsmodels.tsa.seasonal import seasonal_decompose

def calculate_seasonal_decomposition(series, model="additive", period=4):
    """
    Calculate seasonal decomposition for a time series.
    
    Args:
        series (pd.Series): Time series data
        model (str): Type of seasonal component ('additive' or 'multiplicative')
        period (int): Number of periods in a seasonal cycle
        
    Returns:
        dict: Dictionary containing all calculated components
    """
    result = {
        'success': False,
        'error': None,
        'components': {}
    }
    
    try:
        # Perform seasonal decomposition
        decomposition = seasonal_decompose(
            series,
            model=model,
            period=period
        )
        
        # Store z-scored components only
        result['components']['trend'] = decomposition.trend
        result['components']['seasonal'] = decomposition.seasonal
        result['components']['residual'] = decomposition.resid
        
        result['success'] = True
        
    except Exception as e:
        result['error'] = str(e)
    
    return result

def plot_seasonal_decomposition(ngram, series, model="additive", period=4):
    """
    Plots seasonal decomposition (trend, seasonal, residual) for an n-gram time series
    with statistical thresholds for residuals.
    
    Args:
        ngram (str): N-gram to analyze
        series (pd.Series): Time series data for the n-gram
        model (str): Decomposition model ("additive" or "multiplicative")
        period (int): Number of periods in a seasonal cycle
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    decomposition_result = calculate_seasonal_decomposition(series, model=model, period=period)

    if not decomposition_result["success"]:
        raise ValueError(f"Decomposition failed: {decomposition_result['error']}")

    # Drop NaNs to align all components
    trend = decomposition_result["components"]["trend"]
    seasonal = decomposition_result["components"]["seasonal"]
    residual = decomposition_result["components"]["residual"]

    # Use common cleaned index for plotting
    valid_index = trend.index
    
    # Get threshold from session state if available, otherwise use default
    threshold = st.session_state.selected_criteria.get('seasonal_threshold', 2.0)
    
    # Calculate statistics for residuals for thresholding
    residual_mean = residual.mean()
    residual_std = residual.std()
    
    # Calculate upper and lower thresholds
    upper_threshold = residual_mean + (threshold * residual_std)
    lower_threshold = residual_mean - (threshold * residual_std)

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        subplot_titles=("Trend", "Seasonal", "Residual"),
        vertical_spacing=0.1
    )

    # Plot trend component
    fig.add_trace(
        go.Scatter(
            x=valid_index,
            y=trend.values,
            mode="lines",
            name="Trend",
            line=dict(color="blue")
        ),
        row=1, col=1
    )

    # Plot seasonal component
    fig.add_trace(
        go.Scatter(
            x=valid_index,
            y=seasonal[valid_index].values,
            mode="lines",
            name="Seasonal",
            line=dict(color="green")
        ),
        row=2, col=1
    )

    # Plot residual component
    fig.add_trace(
        go.Scatter(
            x=valid_index,
            y=residual[valid_index].values,
            mode="lines+markers",
            name="Residual",
            line=dict(color="orange")
        ),
        row=3, col=1
    )

    # Add horizontal zero lines to all subplots
    for row in range(1, 4):
        fig.add_hline(
            y=0,
            line_width=1,
            line_dash="dash",
            line_color="gray",
            row=row,
            col=1
        )
    
    # Add mean line for residuals
    fig.add_hline(
        y=residual_mean,
        line_width=1,
        line_dash="dash",
        line_color="gray",
        annotation_text="Mean",
        annotation_position="right",
        row=3,
        col=1
    )
    
    # Add threshold lines for residuals
    fig.add_hline(
        y=upper_threshold,
        line_width=1,
        line_dash="dash",
        line_color="red",
        annotation_text=f"+{threshold:.1f}σ",
        annotation_position="top right",
        row=3,
        col=1
    )
    
    fig.add_hline(
        y=lower_threshold,
        line_width=1,
        line_dash="dash",
        line_color="red",
        annotation_text=f"-{threshold:.1f}σ",
        annotation_position="bottom right",
        row=3,
        col=1
    )

    # Layout - increase height for better visibility
    fig.update_layout(
        height=900,  # Increased from 800 to 900
        title=f"Seasonal Decomposition for '{ngram}'",
        hovermode="x unified",
        showlegend=False,
        margin=dict(l=10, r=10, t=50, b=50, pad=0)  # Minimize horizontal margins
    )

    # Set x-axis ticks based on valid index and optimize layout
    for i in range(1, 4):
        fig.update_xaxes(
            tickmode="array",
            tickvals=list(valid_index),
            tickangle=270,
            row=i,
            col=1,
            automargin=True,
            constrain="domain"
        )
        
        # Update y-axis titles for each component
        if i == 1:
            fig.update_yaxes(title_text="Trend", row=i, col=1)
        elif i == 2:
            fig.update_yaxes(title_text="Seasonal", row=i, col=1)
        else:
            fig.update_yaxes(title_text="Residual", row=i, col=1)
    
    # Only add x-axis title to bottom subplot
    fig.update_xaxes(title_text="Quarter", row=3, col=1)

    return fig