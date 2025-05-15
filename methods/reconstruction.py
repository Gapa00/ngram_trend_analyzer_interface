import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def reconstruct_from_pca(pca_model, ngram_idx, original_df):
    # Get the n-gram's PCA coordinates
    ngram_coords = pca_model.transform([original_df.iloc[ngram_idx].values])[0]
    
    # Reconstruct the time series
    reconstructed = pca_model.inverse_transform([ngram_coords])[0]
    
    return reconstructed

def plot_original_vs_reconstructed(original_series, reconstructed_series, ngram, quarters):
    fig = make_subplots(rows=1, cols=1)
    
    # Add original time series
    fig.add_trace(
        go.Scatter(
            x=quarters,
            y=original_series,
            mode="lines+markers",
            name="Original",
            line=dict(color="blue")
        )
    )
    
    # Add reconstructed time series
    fig.add_trace(
        go.Scatter(
            x=quarters,
            y=reconstructed_series,
            mode="lines+markers",
            name="Reconstructed",
            line=dict(color="red", dash="dash")
        )
    )
    
    # Update layout
    fig.update_layout(
        title=f"Original vs. Reconstructed Time Series for '{ngram}'",
        xaxis_title="Quarter",
        yaxis_title="Normalized Value",
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Show only a subset of x-axis labels for readability
    fig.update_xaxes(
        tickmode="array",
        tickvals=[quarters[i] for i in range(0, len(quarters), 4)],
        tickangle=45
    )
    
    return fig