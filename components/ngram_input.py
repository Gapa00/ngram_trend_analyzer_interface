import streamlit as st

def init_analysis_params():
    defaults = {
        'pct_change': True,
        'pct_change_period': 4,
        'pct_change_threshold': 2.0,
        'macd': True,
        'short_period': 4,
        'long_period': 8,
        'signal_period': 3,
        'macd_threshold': 2.0,
        'exp_smoothing': True,
        'exp_trend': 'add',
        'exp_seasonal': 'add',
        'exp_seasonal_period': 4,
        'exp_smoothing_threshold': 2.0,
        'seasonal': True,
        'seasonal_model': 'additive',
        'seasonal_period': 4,
        'seasonal_threshold': 2.0,
        'zone_threshold': 0.1,
    }
    for k, v in defaults.items():
        if 'selected_criteria' not in st.session_state:
            st.session_state.selected_criteria = {}
        if k not in st.session_state.selected_criteria:
            st.session_state.selected_criteria[k] = v

def validate_ngram_input(df, ngram_input):
    if not ngram_input:
        return False, None, []
    
    exact_match_found = False
    original_index = None
    
    for idx in df.index:
        if str(idx).lower() == ngram_input.lower():
            exact_match_found = True
            original_index = idx
            break
    
    if not exact_match_found:
        partial_matches = [
            str(idx) for idx in df.index 
            if ngram_input.lower() in str(idx).lower() and str(idx).lower() != ngram_input.lower()
        ]
        return False, None, partial_matches
    
    return True, original_index, []

def render_ngram_input(df):
    # Initialize session state variables
    if 'shared_ngram' not in st.session_state:
        st.session_state.shared_ngram = ""
    if 'ngram_series' not in st.session_state:
        st.session_state.ngram_series = None
    if 'original_ngram_index' not in st.session_state:
        st.session_state.original_ngram_index = None

    # Initialize analysis parameters
    init_analysis_params()
    
    # Create callback handler function
    def update_param(param_name):
        def callback():
            st.session_state.selected_criteria[param_name] = st.session_state[f"widget_{param_name}"]
        return callback

    dashboard = st.container()

    with dashboard:
        prev_value = st.session_state.shared_ngram
        ngram_input = st.text_input(
            "Search n-gram:",
            value=prev_value,
            key="global_ngram_input"
        )

        if ngram_input != prev_value:
            st.session_state.shared_ngram = ngram_input
            st.session_state.ngram_series = None
            st.session_state.original_ngram_index = None
            st.rerun()

        is_valid, original_index, partial_matches = validate_ngram_input(df, ngram_input)

        if ngram_input:
            if is_valid:
                st.success(f"Found exact match: '{original_index}' ✓")

                if st.session_state.original_ngram_index != original_index:
                    st.session_state.original_ngram_index = original_index
                    st.session_state.ngram_series = df.loc[original_index]

                if st.session_state.original_ngram_index:

                    with st.expander("Configure Criteria Functions Parameters", expanded=False):
                        method_tabs = st.tabs(["Percent Change", "MACD", "Exponential Smoothing", "Seasonal Decomp."])

                        # --- Tab 1: Percent Change ---
                        with method_tabs[0]:
                            # Set initial widget value from session state
                            if "widget_pct_change" not in st.session_state:
                                st.session_state["widget_pct_change"] = st.session_state.selected_criteria['pct_change']
                                
                            show_pct_change = st.checkbox(
                                "Enable Percent Change Analysis",
                                key="widget_pct_change",
                                on_change=update_param("pct_change")
                            )
                            
                            if show_pct_change:
                                col1, col2 = st.columns(2)
                                with col1:
                                    # Set initial widget value
                                    if "widget_pct_change_period" not in st.session_state:
                                        st.session_state["widget_pct_change_period"] = st.session_state.selected_criteria['pct_change_period']
                                        
                                    st.slider(
                                        "Periods for Percent Change",
                                        min_value=1,
                                        max_value=8,
                                        key="widget_pct_change_period",
                                        on_change=update_param("pct_change_period")
                                    )
                                    
                                with col2:
                                    # Set initial widget value
                                    if "widget_pct_change_threshold" not in st.session_state:
                                        st.session_state["widget_pct_change_threshold"] = st.session_state.selected_criteria['pct_change_threshold']
                                        
                                    st.slider(
                                        "Significant Change Threshold",
                                        min_value=0.1,
                                        max_value=5.0,
                                        step=0.1,
                                        key="widget_pct_change_threshold",
                                        on_change=update_param("pct_change_threshold")
                                    )

                        # --- Tab 2: MACD ---
                        with method_tabs[1]:
                            # Set initial widget value
                            if "widget_macd" not in st.session_state:
                                st.session_state["widget_macd"] = st.session_state.selected_criteria['macd']
                                
                            show_macd = st.checkbox(
                                "Enable MACD Analysis",
                                key="widget_macd",
                                on_change=update_param("macd")
                            )
                            
                            if show_macd:
                                col1, col2 = st.columns(2)
                                with col1:
                                    # Set initial widget value
                                    if "widget_short_period" not in st.session_state:
                                        st.session_state["widget_short_period"] = st.session_state.selected_criteria['short_period']
                                        
                                    st.slider(
                                        "Short Period (Fast)",
                                        min_value=2,
                                        max_value=12,
                                        key="widget_short_period",
                                        on_change=update_param("short_period")
                                    )

                                    # Set initial widget value
                                    if "widget_signal_period" not in st.session_state:
                                        st.session_state["widget_signal_period"] = st.session_state.selected_criteria['signal_period']
                                        
                                    st.slider(
                                        "Signal Period",
                                        min_value=2,
                                        max_value=9,
                                        key="widget_signal_period",
                                        on_change=update_param("signal_period")
                                    )

                                with col2:
                                    # Set initial widget value
                                    if "widget_long_period" not in st.session_state:
                                        st.session_state["widget_long_period"] = st.session_state.selected_criteria['long_period']
                                        
                                    st.slider(
                                        "Long Period (Slow)",
                                        min_value=4,
                                        max_value=24,
                                        key="widget_long_period",
                                        on_change=update_param("long_period")
                                    )

                                    # Set initial widget value
                                    if "widget_macd_threshold" not in st.session_state:
                                        st.session_state["widget_macd_threshold"] = st.session_state.selected_criteria['macd_threshold']
                                        
                                    st.slider(
                                        "Histogram Threshold",
                                        min_value=0.1,
                                        max_value=5.0,
                                        step=0.1,
                                        format="%.3f",
                                        key="widget_macd_threshold",
                                        on_change=update_param("macd_threshold")
                                    )

                        # --- Tab 3: Exponential Smoothing ---
                        with method_tabs[2]:
                            # Set initial widget value
                            if "widget_exp_smoothing" not in st.session_state:
                                st.session_state["widget_exp_smoothing"] = st.session_state.selected_criteria['exp_smoothing']
                                
                            show_exp_smoothing = st.checkbox(
                                "Enable Exponential Smoothing Analysis",
                                key="widget_exp_smoothing",
                                on_change=update_param("exp_smoothing")
                            )
                            
                            if show_exp_smoothing:
                                col1, col2 = st.columns(2)
                                with col1:
                                    trend_options = [None, "add", "mul"]
                                    
                                    # Get the current index
                                    current_trend_idx = trend_options.index(st.session_state.selected_criteria['exp_trend'])
                                    
                                    # Define a callback for this specific dropdown
                                    def update_exp_trend():
                                        selected_idx = st.session_state["widget_exp_trend"]
                                        st.session_state.selected_criteria['exp_trend'] = trend_options[selected_idx]
                                    
                                    # Set initial widget value
                                    if "widget_exp_trend" not in st.session_state:
                                        st.session_state["widget_exp_trend"] = current_trend_idx
                                        
                                    st.selectbox(
                                        "Trend Component",
                                        options=range(len(trend_options)),
                                        format_func=lambda i: "None" if trend_options[i] is None else trend_options[i].capitalize(),
                                        key="widget_exp_trend",
                                        on_change=update_exp_trend
                                    )

                                with col2:
                                    seasonal_options = [None, "add", "mul"]
                                    
                                    # Get the current index
                                    current_seasonal_idx = seasonal_options.index(st.session_state.selected_criteria['exp_seasonal'])
                                    
                                    # Define a callback for this specific dropdown
                                    def update_exp_seasonal():
                                        selected_idx = st.session_state["widget_exp_seasonal"]
                                        st.session_state.selected_criteria['exp_seasonal'] = seasonal_options[selected_idx]
                                    
                                    # Set initial widget value
                                    if "widget_exp_seasonal" not in st.session_state:
                                        st.session_state["widget_exp_seasonal"] = current_seasonal_idx
                                        
                                    st.selectbox(
                                        "Seasonal Component",
                                        options=range(len(seasonal_options)),
                                        format_func=lambda i: "None" if seasonal_options[i] is None else seasonal_options[i].capitalize(),
                                        key="widget_exp_seasonal",
                                        on_change=update_exp_seasonal
                                    )

                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.session_state.selected_criteria['exp_seasonal']:
                                        # Set initial widget value
                                        if "widget_exp_seasonal_period" not in st.session_state:
                                            st.session_state["widget_exp_seasonal_period"] = st.session_state.selected_criteria['exp_seasonal_period']
                                            
                                        st.slider(
                                            "Seasonal Periods",
                                            min_value=2,
                                            max_value=8,
                                            key="widget_exp_seasonal_period",
                                            on_change=update_param("exp_seasonal_period")
                                        )
                                        
                                with col2:
                                    # Set initial widget value
                                    if "widget_exp_smoothing_threshold" not in st.session_state:
                                        st.session_state["widget_exp_smoothing_threshold"] = st.session_state.selected_criteria['exp_smoothing_threshold']
                                        
                                    st.slider(
                                        "Residual Threshold (σ)",
                                        min_value=0.1,
                                        max_value=5.0,
                                        step=0.1,
                                        key="widget_exp_smoothing_threshold",
                                        on_change=update_param("exp_smoothing_threshold")
                                    )

                        # --- Tab 4: Seasonal Decomposition ---
                        with method_tabs[3]:
                            # Set initial widget value
                            if "widget_seasonal" not in st.session_state:
                                st.session_state["widget_seasonal"] = st.session_state.selected_criteria['seasonal']
                                
                            show_seasonal = st.checkbox(
                                "Enable Seasonal Decomposition Analysis",
                                key="widget_seasonal",
                                on_change=update_param("seasonal")
                            )
                            
                            if show_seasonal:
                                col1, col2 = st.columns(2)
                                with col1:
                                    model_options = ["additive", "multiplicative"]
                                    
                                    # Get the current index
                                    current_model_idx = model_options.index(st.session_state.selected_criteria['seasonal_model'])
                                    
                                    # Define a callback for this specific dropdown
                                    def update_seasonal_model():
                                        selected_idx = st.session_state["widget_seasonal_model"]
                                        st.session_state.selected_criteria['seasonal_model'] = model_options[selected_idx]
                                    
                                    # Set initial widget value
                                    if "widget_seasonal_model" not in st.session_state:
                                        st.session_state["widget_seasonal_model"] = current_model_idx
                                        
                                    st.selectbox(
                                        "Decomposition Model",
                                        options=range(len(model_options)),
                                        format_func=lambda i: model_options[i].capitalize(),
                                        key="widget_seasonal_model",
                                        on_change=update_seasonal_model
                                    )
                                    
                                    # Set initial widget value for seasonal period
                                    if "widget_seasonal_period" not in st.session_state:
                                        st.session_state["widget_seasonal_period"] = st.session_state.selected_criteria['seasonal_period']
                                        
                                    st.slider(
                                        "Seasonal Periods",
                                        min_value=2,
                                        max_value=8,
                                        key="widget_seasonal_period",
                                        on_change=update_param("seasonal_period")
                                    )
                                    
                                with col2:
                                    # Set initial widget value for seasonal threshold
                                    if "widget_seasonal_threshold" not in st.session_state:
                                        st.session_state["widget_seasonal_threshold"] = st.session_state.selected_criteria['seasonal_threshold']
                                        
                                    st.slider(
                                        "Residual Threshold (σ)",
                                        min_value=0.1,
                                        max_value=5.0,
                                        step=0.1,
                                        key="widget_seasonal_threshold",
                                        on_change=update_param("seasonal_threshold")
                                    )

                return original_index
            else:
                st.session_state.ngram_series = None
                st.session_state.original_ngram_index = None

                if partial_matches:
                    if len(partial_matches) < 20:
                        st.write("Similar matches:")
                        cols = st.columns(min(5, len(partial_matches)))
                        for i, ngram in enumerate(partial_matches[:20]):
                            with cols[i % len(cols)]:
                                if st.button(ngram, key=f"btn_{ngram}_{i}"):
                                    st.session_state.shared_ngram = ngram
                                    st.rerun()
                    else:
                        st.info(f"Found {len(partial_matches)} similar matches. Please refine your search.")
                else:
                    st.warning(f"No n-grams found matching '{ngram_input}'")

    return None