import numpy as np
import pandas as pd
import streamlit as st
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
import plotly.express as px
import plotly.graph_objects as go
from utils.cache_utils import get_cached_result, save_cached_result

@st.cache_data
def compute_pca(df, n_components=2):
    # Check if result is cached
    cache_key = f"pca_{n_components}_{df.shape[0]}_{df.shape[1]}"
    cached = get_cached_result(cache_key)
    if cached is not None:
        return cached
    
    # POTENCIALNO, bi lahko se standardizirali podatke, preden jih damo v PCA !!!
    # Convert DataFrame to numpy array for PCA
    X = df.values
    
    # Compute PCA
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(X)
    
    # Create a DataFrame for the result
    result_df = pd.DataFrame(
        pca_result,
        columns=[f"PC{i+1}" for i in range(n_components)],
        index=df.index
    )
    
    # Cache the result
    save_cached_result(cache_key, (result_df, pca, pca.explained_variance_ratio_))
    
    return result_df, pca, pca.explained_variance_ratio_

@st.cache_data
def compute_tsne(df, n_components=2, perplexity=30, max_iter=1000):
     # Check if result is cached
    cache_key = f"tsne_{n_components}_{perplexity}_{max_iter}_{df.shape[0]}_{df.shape[1]}"
    cached = get_cached_result(cache_key)
    if cached is not None:
        return cached
    
    # POTENCIALNO, bi lahko se standardizirali podatke, preden jih damo v t-SNE !!!
    X = df.values
    
    # Compute t-SNE
    tsne = TSNE(n_components=n_components, perplexity=perplexity, max_iter=max_iter, random_state=42)
    tsne_result = tsne.fit_transform(X)
    
    # Create a DataFrame for the result
    result_df = pd.DataFrame(
        tsne_result,
        columns=[f"TSNE{i+1}" for i in range(n_components)],
        index=df.index
    )
    
    # Cache the result
    save_cached_result(cache_key, result_df)
    
    return result_df

@st.cache_data
def compute_umap(df, n_neighbors=15, min_dist=0.1):

    # Check if result is cached
    cache_key = f"umap_{n_neighbors}_{min_dist}_{df.shape[0]}_{df.shape[1]}"
    cached = get_cached_result(cache_key)
    if cached is not None:
        return cached
    
    # POTENCIALNO, bi lahko se standardizirali podatke, preden jih damo v UMAP !!!
    X = df.values
    
    # Compute UMAP
    reducer = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist)
    umap_result = reducer.fit_transform(X)
    
    # Create a DataFrame for the result
    result_df = pd.DataFrame(
        umap_result,
        columns=["UMAP1", "UMAP2"],
        index=df.index
    )
    
    # Cache the result
    save_cached_result(cache_key, result_df)
    
    return result_df

def plot_dimensionality_reduction(result_df, title, highlight_ngram=None):
    plot_df = result_df.copy()
    
    if highlight_ngram and highlight_ngram in plot_df.index:
        plot_df["highlight"] = "Other"
        plot_df.loc[highlight_ngram, "highlight"] = highlight_ngram
        
        # Create figure with highlighted point
        fig = px.scatter(
            plot_df.reset_index(), 
            x=plot_df.columns[0], 
            y=plot_df.columns[1],
            hover_name="n-gram",
            color="highlight",
            color_discrete_map={highlight_ngram: "red", "Other": "lightgrey"},
            title=title
        )
    else:
        # Create figure without highlighting
        fig = px.scatter(
            plot_df.reset_index(), 
            x=plot_df.columns[0], 
            y=plot_df.columns[1],
            hover_name="n-gram",
            title=title
        )
    
    # Update layout
    fig.update_layout(
        height=500,
        legend_title_text="",
        legend_orientation="h",
        legend_y=-0.15
    )
    
    return fig

def plot_explained_variance(explained_variance_ratio):
    fig = px.bar(
        x=[f"PC{i+1}" for i in range(len(explained_variance_ratio))],
        y=explained_variance_ratio,
        labels={"x": "Principal Component", "y": "Explained Variance Ratio"},
        title="Explained Variance by Principal Component"
    )
    
    fig.update_layout(
        height=300,
        showlegend=False
    )
    
    return fig