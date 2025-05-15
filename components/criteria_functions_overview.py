import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from methods.criteria_functions.percent_change import plot_percent_change
from methods.criteria_functions.exponential_smoothing import plot_exponential_smoothing
from methods.criteria_functions.seasonal_decomposition import plot_seasonal_decomposition
from methods.criteria_functions.macd import plot_macd
from utils.helper_functions import plot_original_series

def render_criteria_functions(df):
    """
    Render the N-gram Analysis page
    
    Args:
        df (pd.DataFrame): DataFrame with n-grams as index and quarters as columns
    """
    st.header("Criteria Functions")
    
    if df is None or df.empty:
        st.error("No data available for analysis.")
        return
    
    # Initialize show_analysis flag if not exists
    if 'show_analysis' not in st.session_state:
        st.session_state.show_analysis = False
    
    # Get selected criteria from session state
    selected_criteria = st.session_state.selected_criteria
    
    # Check if we have a valid n-gram and series in session state
    valid_ngram = 'original_ngram_index' in st.session_state and st.session_state.original_ngram_index is not None
    
    if not valid_ngram:
        st.warning("Please select a valid n-gram from the search box above.")
        return
    
    # Analysis button
    if st.button(
        "Analyze", 
        type="primary", 
        use_container_width=True,
        key="analyze_button"
    ):
        # Set the show_analysis flag in session state
        st.session_state.show_analysis = True
    
    # Show analysis if button was clicked
    if st.session_state.show_analysis:
        original_index = st.session_state.original_ngram_index
        ngram_series = st.session_state.ngram_series
        
        # Plot original series first
        with st.spinner("Rendering original series..."):
            original_fig = plot_original_series(original_index, ngram_series)
            st.plotly_chart(original_fig, use_container_width=True)
        
        # Percent Change analysis
        if selected_criteria.get('pct_change', False):
            with st.spinner("Computing percent change..."):
                try:
                    pct_change_fig = plot_percent_change(
                        original_index, 
                        ngram_series,
                        periods=selected_criteria.get('pct_change_period', 4),
                        threshold=selected_criteria.get('pct_change_threshold', 0.2)
                    )
                    
                    st.plotly_chart(pct_change_fig, use_container_width=True)
                
                except Exception as e:
                    st.error(f"Error in percent change analysis: {e}")
        
        # MACD analysis
        if selected_criteria.get('macd', False):
            with st.spinner("Computing MACD..."):
                try:
                    macd_fig = plot_macd(
                        original_index, 
                        ngram_series,
                        fast_period=selected_criteria.get('short_period', 4),
                        slow_period=selected_criteria.get('long_period', 8),
                        signal_period=selected_criteria.get('signal_period', 3),
                        threshold=selected_criteria.get('macd_threshold', 0.01)
                    )
                    
                    st.plotly_chart(macd_fig, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Error in MACD analysis: {e}")
                    
        # Exponential Smoothing analysis
        if selected_criteria.get('exp_smoothing', False):
            with st.spinner("Computing exponential smoothing..."):
                try:
                    exp_smoothing_fig = plot_exponential_smoothing(
                        original_index, 
                        ngram_series,
                        trend=selected_criteria.get('exp_trend', 'add'),
                        seasonal=selected_criteria.get('exp_seasonal', 'add'),
                        seasonal_periods=selected_criteria.get('exp_seasonal_period', 4)
                    ) 
                    
                    st.plotly_chart(exp_smoothing_fig, use_container_width=True)

                except Exception as e:
                    st.error(f"Error in exponential smoothing analysis: {e}")
        
        # Seasonal Decomposition analysis
        if selected_criteria.get('seasonal', False):
            with st.spinner("Computing seasonal decomposition..."):
                try:
                    seasonal_fig = plot_seasonal_decomposition(
                        original_index, 
                        ngram_series,
                        model=selected_criteria.get('seasonal_model', 'additive'),
                        period=selected_criteria.get('seasonal_period', 4)
                    )
                    
                    st.plotly_chart(seasonal_fig, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Error in seasonal decomposition analysis: {e}")