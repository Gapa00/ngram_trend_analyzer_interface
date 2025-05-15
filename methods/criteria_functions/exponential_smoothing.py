import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def calculate_exponential_smoothing(series, trend, seasonal, seasonal_periods):
    """
    Calculate exponential smoothing components for a time series.
    
    Args:
        series (pd.Series): Time series data
        trend (str): Trend component type ('add', 'mul', or None)
        seasonal (str): Seasonal component type ('add', 'mul', or None)
        seasonal_periods (int): Number of periods in a seasonal cycle
        
    Returns:
        dict: Dictionary containing all calculated components
    """
    # Create and fit model on original data
    model = ExponentialSmoothing(
        series,
        trend=trend,
        seasonal=seasonal,
        seasonal_periods=seasonal_periods if seasonal else None
    )
    
    result = {
        'success': False,
        'error': None,
        'components': {},
        'forecast': None
    }
    
    try:
        fitted_model = model.fit()
        
        # Store only z-scored values
        result['components']['fitted'] = fitted_model.fittedvalues
        
        # Level component
        if hasattr(fitted_model, 'level'):
            result['components']['level'] = fitted_model.level
        
        # Trend component
        if trend and hasattr(fitted_model, 'trend'):
            result['components']['trend'] = fitted_model.trend
        
        # Seasonal component
        if seasonal and hasattr(fitted_model, 'season'):
            result['components']['seasonal'] = fitted_model.season
        
        # Residuals
        residuals = series - fitted_model.fittedvalues
        result['components']['residuals'] = residuals
        
        # Generate forecast if possible
        forecast_periods = 4
        try:
            # Generate forecast
            forecast_values = fitted_model.forecast(forecast_periods)
            
            # Create forecast quarter labels
            last_quarter = series.index[-1]
            year = int(last_quarter.split('Q')[0])
            quarter = int(last_quarter.split('Q')[1])
            
            forecast_index = []
            for i in range(forecast_periods):
                quarter += 1
                if quarter > 4:
                    quarter = 1
                    year += 1
                forecast_index.append(f"{year}Q{quarter}")
            
            # Create a Series for the forecast
            forecast_series = pd.Series(forecast_values, index=forecast_index)
            
            result['forecast'] = {
                'values': forecast_series,
                'index': forecast_index
            }
        except Exception as e:
            # Just leave forecast as None if it fails
            pass
        
        result['success'] = True
        
    except Exception as e:
        result['error'] = str(e)
    
    return result

def plot_exponential_smoothing(ngram, series, trend, seasonal, seasonal_periods):
    """
    Plot exponential smoothing for an n-gram with each component on its own graph,
    with statistical thresholds for residuals similar to other plots.
    
    Args:
        ngram (str): N-gram name
        series (pd.Series): Time series data for the n-gram
        trend (str): Trend component type ('add', 'mul', or None)
        seasonal (str): Seasonal component type ('add', 'mul', or None)
        seasonal_periods (int): Number of periods in a seasonal cycle
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    # Calculate metrics
    result = calculate_exponential_smoothing(series, trend, seasonal, seasonal_periods)
    
    if not result['success']:
        st.error(f"Error in exponential smoothing: {result['error']}")
        return None
    
    # Determine number of subplots needed
    num_components = len(result['components'])
    if result['forecast'] is not None:
        num_components += 1  # Add one more for forecast
    
    # Create subplot titles
    subplot_titles = []
    for component in result['components']:
        subplot_titles.append(component.capitalize())
    if result['forecast'] is not None:
        subplot_titles.append("Forecast")
    
    # Create figure with subplots - one for each component
    fig = make_subplots(
        rows=num_components, 
        cols=1,
        subplot_titles=subplot_titles,
        vertical_spacing=0.05,  # Reduce spacing between plots
        shared_xaxes=True
    )
    
    # Create combined x-axis range
    all_x_values = list(series.index)
    if result['forecast'] is not None and result['forecast']['index']:
        all_x_values.extend(result['forecast']['index'])
    
    # Get threshold from session state if available, otherwise use default
    threshold = st.session_state.selected_criteria.get('exp_smoothing_threshold', 2.0)
    
    # Add each component to its own subplot
    row = 1
    colors = {"fitted": "red", "level": "purple", "trend": "orange", 
              "seasonal": "green", "residuals": "blue"}
    
    for component, data in result['components'].items():
        # Special handling for residuals
        if component == "residuals":
            # Calculate mean and standard deviation of residuals
            residuals_mean = data.mean()
            residuals_std = data.std()
            
            # Calculate upper and lower thresholds
            upper_threshold = residuals_mean + (threshold * residuals_std)
            lower_threshold = residuals_mean - (threshold * residuals_std)
            
            # Add residuals line
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data.values,
                    mode="lines+markers",
                    line=dict(color="blue", width=2),
                    name="Residuals"
                ),
                row=row, col=1
            )
            
            # Add threshold lines
            fig.add_hline(
                y=upper_threshold, 
                line_width=1, 
                line_dash="dash", 
                line_color="red",
                annotation_text=f"+{threshold:.1f}σ",
                annotation_position="top right",
                row=row, col=1
            )
            
            fig.add_hline(
                y=lower_threshold, 
                line_width=1, 
                line_dash="dash", 
                line_color="red",
                annotation_text=f"-{threshold:.1f}σ",
                annotation_position="bottom right",
                row=row, col=1
            )
            
        else:
            # Normal handling for non-residual components
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data.values,
                    mode="lines",
                    name=component.capitalize(),
                    line=dict(color=colors.get(component, "gray"))
                ),
                row=row, col=1
            )
        
        # Add horizontal line at zero for all components
        fig.add_hline(
            y=0, 
            line_width=1, 
            line_dash="dash", 
            line_color="gray",
            row=row, col=1
        )
        
        row += 1
    
    # Add forecast if available
    if result['forecast'] is not None:
        fig.add_trace(
            go.Scatter(
                x=result['forecast']['values'].index,
                y=result['forecast']['values'].values,
                mode="lines+markers",
                name="Forecast",
                line=dict(color="green", width=2)
            ),
            row=row, col=1
        )
        
        # Add horizontal line at zero for forecast
        fig.add_hline(
            y=0, 
            line_width=1, 
            line_dash="dash", 
            line_color="gray",
            row=row, col=1
        )
    
    # Update layout with larger heights
    fig.update_layout(
        title=f"Exponential Smoothing Components for '{ngram}'",
        height=250 * num_components,  # Increase height per component from 150px to 250px
        showlegend=False,
        hovermode="x unified",
        margin=dict(t=50, b=50)  # Adjust margins
    )
    
    # Show x-axis labels only on the bottom subplot
    for i in range(1, num_components + 1):
        # Set y-axis title
        fig.update_yaxes(title_text="Value", row=i, col=1)
        
        # Hide x-axis labels except for bottom plot
        fig.update_xaxes(
            tickmode="array",
            tickvals=all_x_values,
            tickangle=270,
            showticklabels=(i == num_components),  # Only show on bottom subplot
            row=i, col=1
        )
    
    # Add x-axis title only to the bottom subplot
    fig.update_xaxes(title_text="Quarter", row=num_components, col=1)
    
    return fig