import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from methods.dimensionality import (
    compute_pca, 
    compute_tsne, 
    compute_umap, 
    plot_dimensionality_reduction,
    plot_explained_variance
)
from methods.reconstruction import reconstruct_from_pca, plot_original_vs_reconstructed

def render_overview(df):
    """
    Render the General Overview page
    
    Args:
        df (pd.DataFrame): DataFrame with n-grams as index and quarters as columns
    """
    if df is None or df.empty:
        st.error("No data available for analysis.")
        return
        
    st.header("General Overview")
    
    # Use the shared n-gram from session state
    ngram_input = st.session_state.shared_ngram
    
    # Compute dimensionality reductions with loading indicators
    try:
        with st.spinner("Computing PCA..."):
            pca_df, pca_model, explained_variance = compute_pca(df)
            
        with st.spinner("Computing t-SNE..."):
            tsne_df = compute_tsne(df)
            
        with st.spinner("Computing UMAP..."):
            umap_df = compute_umap(df)
    except Exception as e:
        st.error(f"Error in dimensionality reduction: {e}")
        st.warning("Using placeholder visualizations instead.")
        # Create empty DataFrames for placeholders
        pca_df = pd.DataFrame(columns=["PC1", "PC2"])
        pca_model = None
        explained_variance = np.array([])
        tsne_df = pd.DataFrame(columns=["TSNE1", "TSNE2"])
        umap_df = pd.DataFrame(columns=["UMAP1", "UMAP2"])
    
    # Create three columns for the visualizations
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("PCA")
        
        # Plot PCA
        pca_fig = plot_dimensionality_reduction(
            pca_df, 
            "PCA of N-gram Time Series",
            highlight_ngram=ngram_input if ngram_input in df.index else None
        )
        st.plotly_chart(pca_fig, use_container_width=True)
        
        # Plot explained variance
        variance_fig = plot_explained_variance(explained_variance)
        st.plotly_chart(variance_fig, use_container_width=True)
    
    with col2:
        st.subheader("t-SNE")
        
        # Plot t-SNE
        tsne_fig = plot_dimensionality_reduction(
            tsne_df, 
            "t-SNE of N-gram Time Series",
            highlight_ngram=ngram_input if ngram_input in df.index else None
        )
        st.plotly_chart(tsne_fig, use_container_width=True)
    
    with col3:
        st.subheader("UMAP")
        
        # Plot UMAP
        umap_fig = plot_dimensionality_reduction(
            umap_df, 
            "UMAP of N-gram Time Series",
            highlight_ngram=ngram_input if ngram_input in df.index else None
        )
        st.plotly_chart(umap_fig, use_container_width=True)
    
    # Show reconstruction if an n-gram is selected and PCA model exists
    if ngram_input and ngram_input in df.index and pca_model is not None:
        st.header(f"Time Series Reconstruction for '{ngram_input}'")
        
        try:
            with st.spinner("Computing reconstruction..."):
                # Get the original time series
                original_series = df.loc[ngram_input].values
                
                # Get the reconstructed time series from PCA
                ngram_idx = df.index.get_loc(ngram_input)
                reconstructed_series = reconstruct_from_pca(pca_model, ngram_idx, df)
                
                # Plot original vs. reconstructed
                reconstruction_fig = plot_original_vs_reconstructed(
                    original_series, 
                    reconstructed_series, 
                    ngram_input,
                    df.columns.tolist()
                )
                
                st.plotly_chart(reconstruction_fig, use_container_width=True)
                
                # Calculate and display reconstruction error
                mse = np.mean((original_series - reconstructed_series) ** 2)
                st.metric("Mean Squared Error", f"{mse:.4f}")
        except Exception as e:
            st.error(f"Error in reconstruction: {e}")
            st.info("Could not compute the reconstruction for this n-gram.")