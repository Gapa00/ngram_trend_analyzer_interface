import streamlit as st
import pandas as pd
import numpy as np
import math
import plotly.graph_objects as go
from methods.criteria_functions.percent_change import calculate_pct
from methods.criteria_functions.macd import calculate_macd
from methods.criteria_functions.exponential_smoothing import calculate_exponential_smoothing
from methods.criteria_functions.seasonal_decomposition import calculate_seasonal_decomposition
from utils.helper_functions import zs

def analyze_trends(series, selected_criteria):
    results = {}
    signals = pd.DataFrame(index=series.index)
    active_criteria = 0
    
    ## DODAJ PODALJSEVANJE S PROHPET ALI EXP SMOOTHING ##
    
    # 1. Percent Change Analysis
    if selected_criteria.get('pct_change', False):
        active_criteria += 1
        try:
            # Calculate percent change
            period = selected_criteria.get('pct_change_period', 4)
            threshold = selected_criteria.get('pct_change_threshold', 2)
            
            pct_change = zs(series.pct_change(periods=period).dropna())
            signals['pct_change'] = (pct_change > threshold) & (~pd.isna(pct_change))
        except Exception as e:
            results['percent_change'] = {'error': str(e)}
    
    # 2. MACD Analysis
    if selected_criteria.get('macd', False):
        active_criteria += 1
        try:
            fast_period = selected_criteria.get('short_period', 4)
            slow_period = selected_criteria.get('long_period', 8)
            signal_period = selected_criteria.get('signal_period', 3)
            threshold = selected_criteria.get('macd_threshold', 2)
            
            macd_line, signal_line, histogram = calculate_macd(series, fast_period, slow_period, signal_period)
            
            histogram_z = zs(histogram)
            signals['macd_hist'] = (histogram_z > threshold) & (~pd.isna(histogram_z))
        except Exception as e:
            results['macd'] = {'error': str(e)}
    
    # 3. Exponential Smoothing Analysis (focus on forecasts and residuals)
    if selected_criteria.get('exp_smoothing', False):
        active_criteria += 1
        try:
            trend = selected_criteria.get('exp_trend', 'add')
            seasonal = selected_criteria.get('exp_seasonal', 'add')
            seasonal_periods = selected_criteria.get('exp_seasonal_period', 4)
            threshold = selected_criteria.get('exp_smoothing_threshold', 2)
            
            exp_result = calculate_exponential_smoothing(
                series, trend, seasonal, seasonal_periods
            )
            
            if exp_result['success']:
                if 'components' in exp_result and 'residuals' in exp_result['components']:
                    residuals = zs(exp_result['components']['residuals'])
                    signals['exp_smooth'] = residuals > threshold
            else:
                results['exp_smoothing'] = {'error': exp_result['error']}
        except Exception as e:
            results['exp_smoothing'] = {'error': str(e)}
    
    # 4. Seasonal Decomposition Analysis (focus on residuals)
    if selected_criteria.get('seasonal', False):
        active_criteria += 1
        try:
            model = selected_criteria.get('seasonal_model', 'additive')
            period = selected_criteria.get('seasonal_period', 4)
            threshold = selected_criteria.get('seasonal_threshold', 2)
            
            seasonal_result = calculate_seasonal_decomposition(series, model, period)
            
            if seasonal_result['success']:
                if 'components' in seasonal_result and 'residual' in seasonal_result['components']:
                    residual = zs(seasonal_result['components']['residual'])
                    signals['seasonal'] = residual > threshold
            else:
                results['seasonal'] = {'error': seasonal_result['error']}
        except Exception as e:
            results['seasonal'] = {'error': str(e)}
    
    # Calculate consensus (more than half of active criteria agree)
    if active_criteria > 0:
        signals = signals.fillna(False)
        signal_count = signals.sum(axis=1)
        
        threshold = math.ceil(active_criteria / 2.0)
        consensus_points = signal_count[signal_count > threshold].index.tolist()
        
        results['consensus'] = {
            'points': consensus_points,
            'signals': signals,
            'signal_count': signal_count,
            'active_criteria': active_criteria
        }
    return results

def localize_trend_zones(series, consensus_points, threshold):
    """
    Identify localized trend zones starting from consensus points using adaptive thresholding.

    Args:
        series (pd.Series): Original time series.
        consensus_points (list): List of timestamps (indices) indicating signal agreement.
        threshold (float): Scaling factor for adaptive threshold.
    
    Returns:
        (go.Figure, list): Tuple of Plotly figure and list of trendy quarter indices.
    """
    if not consensus_points:
        return go.Figure(), []

    # 1. Smoothed trend derivative and z-scoring
    ma = series.rolling(window=4, min_periods=1).mean()
    ma_diff = ma.diff()
    trend_line = ma_diff.rolling(window=4, min_periods=1).mean().dropna()
    z_trend_line = zs(trend_line)

    # 2. Adaptive threshold
    max_abs_derivative = z_trend_line.abs().max()

    # 3. Detect zones around consensus points
    used_indices = set()
    final_zones = []

    for cp in consensus_points:
        if cp not in z_trend_line.index or cp in used_indices:
            continue
        
        zone = [cp]
        idx_list = z_trend_line.index.tolist()
        cp_idx = idx_list.index(cp)

        # Expand left
        left_idx = cp_idx - 1
        while left_idx >= 0:
            ts = idx_list[left_idx]
            if z_trend_line[ts] >= threshold and ts not in used_indices:
                zone.insert(0, ts)
                left_idx -= 1
            else:
                break

        # Expand right
        right_idx = cp_idx + 1
        while right_idx < len(idx_list):
            ts = idx_list[right_idx]
            if z_trend_line[ts] >= threshold and ts not in used_indices:
                zone.append(ts)
                right_idx += 1
            else:
                break

        # Mark indices as used and save zone
        final_zones.append(zone)
        used_indices.update(zone)

    # 4. Plotting
    z_series = zs(series)
    fig = go.Figure()

    # Plot z-scored series
    fig.add_trace(go.Scatter(x=z_series.index, y=z_series.values,
                             name="Z-Series", line=dict(color="gray")))

    # Plot z-trend line
    fig.add_trace(go.Scatter(x=z_trend_line.index, y=z_trend_line.values,
                             name="Z-Trend Line", line=dict(color="orange")))

    # Plot adaptive threshold lines
    fig.add_trace(go.Scatter(x=z_trend_line.index, y=[threshold] * len(z_trend_line),
                             name="Threshold", line=dict(color="red", dash="dash")))

    # Shade trend zones
    for zone in final_zones:
        fig.add_vrect(
            x0=zone[0], x1=zone[-1],
            fillcolor="rgba(0, 200, 0, 0.1)", line_width=0, layer="below"
        )

    fig.update_layout(
        title="Localized Trend Zones",
        xaxis_title="Quarter",
        yaxis_title="Z-Score",
        hovermode="x unified",
        showlegend=True,
        height=500
    )

    # Flatten zone indices
    trendy_quarters = sorted(set(i for zone in final_zones for i in zone))

    return fig, trendy_quarters


def render_trend_detection(df):
    st.header("Trend Detection")
    
    if df is None or df.empty:
        st.error("No data available for analysis.")
        return
    
    # Check if we have a valid n-gram selected and its series
    valid_ngram = 'original_ngram_index' in st.session_state and st.session_state.original_ngram_index is not None
    
    if not valid_ngram:
        st.warning("Please select a valid n-gram from the search box above.")
        return
    
    # Get the n-gram and series from session state
    original_index = st.session_state.original_ngram_index
    series = st.session_state.ngram_series
    
    # Get selected criteria from session state
    selected_criteria = st.session_state.selected_criteria
    
    # Add zone threshold if not already present
    if 'zone_threshold' not in selected_criteria:
        selected_criteria['zone_threshold'] = 0.5
    
    # Create tabs
    tab1, tab2 = st.tabs(["Individual Trend Analysis", "Hotness Leaderboard"])
    
    with tab1:
        # Configuration section
        with st.expander("Configure Trend Hill Detection Threshold", expanded=False):
            # Zone expansion threshold slider
            selected_criteria['zone_threshold'] = st.slider(
                "Trend Hill, Derivative Threshold",
                min_value=0.01,
                max_value=1.0,
                value=selected_criteria.get('zone_threshold', 0.1),
                step=0.01,
                help="Lower value expands trend zones more, higher value makes trend zones more focused"
            )
        
        # Analysis button
        if st.button(
            "Analyze", 
            type="primary", 
            use_container_width=True
        ):            
            # Run the consolidated analysis
            with st.spinner("Analyzing trends across all selected criteria..."):
                results = analyze_trends(series, selected_criteria)
                
                # Store results in session state
                st.session_state.trend_analysis_results = results
                
                # Display consensus findings
                if 'consensus' in results:
                    consensus = results['consensus']
                    consensus_points = consensus['points']
                    
                    if len(consensus_points) > 0:
                        st.subheader("Signal Heatmap")
                        
                        # Convert boolean signals to numeric for better visualization
                        heatmap_data = consensus['signals'].astype(int)
                        
                        # Create a heatmap using Plotly
                        fig = go.Figure(data=go.Heatmap(
                            z=heatmap_data.T.values,
                            x=heatmap_data.index,
                            y=heatmap_data.columns,
                            colorscale=[[0, "rgba(50, 50, 60, 0.8)"], [1, "rgba(0, 230, 130, 0.9)"]],
                            showscale=False
                        ))
                        
                        fig.update_layout(
                            title="Signal Activation Across Criteria Functions",
                            xaxis_title="Quarter",
                            yaxis_title="Method",
                            height=300,
                            margin=dict(l=50, r=50, t=50, b=50),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Immediately show trend zones analysis
                        st.subheader("Trend Zones")
                        with st.spinner("Identifying trend zones..."):
                            # Apply the localize_trend_zones function
                            trend_fig, trendy_quarters = localize_trend_zones(
                                series, 
                                consensus_points, 
                                selected_criteria.get('zone_threshold', 0.5)
                            )
                            
                            # Display the visualization
                            st.plotly_chart(trend_fig, use_container_width=True)
                            
                            # Show summary of trendy quarters
                            if trendy_quarters:
                                st.success(f"Identified {len(trendy_quarters)} quarters in trend zones")
                                
                                # Display quarters in a more visually appealing way
                                st.write("Quarters with identified trends:")
                                
                                # Create columns for displaying quarters
                                cols = st.columns(4)  # Display 4 quarters per row
                                
                                for i, quarter in enumerate(trendy_quarters):
                                    with cols[i % 4]:
                                        st.markdown(f"**{quarter}**")
                            else:
                                st.warning("No trend zones identified. Try adjusting the zone threshold.")
                    else:
                        st.warning("No consensus trend signals found where majority of criteria agree.")
                    
                    # Summary of active criteria
                    st.write(f"Analysis used {consensus['active_criteria']} active criteria functions.")
                else:
                    st.error("No consensus analysis could be performed. Please ensure at least one analysis method is enabled.")
    
    with tab2:
        # Placeholder for leaderboard (to be implemented later)
        st.info("Hotness Leaderboard will be implemented in the future.")