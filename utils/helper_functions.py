import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import zscore

def zs(s): return pd.Series(zscore(s.dropna()), index=s.dropna().index)

def plot_original_series(ngram, series):
    fig = go.Figure()
    
    # Add time series line
    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=series,
            mode="lines+markers",
            name="Original Series",
            line=dict(color="blue", width=2)
        )
    )
    
    # Update layout
    fig.update_layout(
        title=f"Time Series for '{ngram}'",
        xaxis_title="Quarter",
        yaxis_title="Normalized Frequency",
        height=400,
        hovermode="x unified",
        template="plotly_white"  # Clean white background template
    )
    
    # Show all x-axis labels
    fig.update_xaxes(
        tickmode="array",
        tickvals=list(series.index),
        tickangle=270
    )
    
    return fig