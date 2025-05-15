import streamlit as st
import pandas as pd
import os	
from components.navbar import create_navbar
from components.general_overview import render_overview
from components.criteria_functions_overview import render_criteria_functions
from components.trend_detection_overview import render_trend_detection
from components.ngram_input import render_ngram_input
from utils.data_loader import load_data
from settings import NGRAM_DATASET_PATH

def main():
    # Set page config
    st.set_page_config(
        page_title="N-Gram Trend Analysis",
        page_icon="📊",
        layout="wide",
    )
    
    # Add custom CSS
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 16px;
            border-radius: 4px 4px 0px 0px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.title("N-Gram Trend Analysis Dashboard")
    
    # Description text
    st.markdown("""
    This dashboard analyzes temporal patterns in term frequencies across quarterly data to identify 
    emerging "hot" n-grams through advanced statistical techniques.

    **Usage Guide:**
    1. Enter a specific n-gram in the search box
    2. Adjust parameters for various criteria functions to fine-tune analysis sensitivity
    3. Examine trend signals generated through consensus voting of statistical outliers across criteria functions
    4. Visualize precise trend intervals detected via smoothed derivative analysis with z-score thresholding
    
    ___
    """)

    # Initialize shared n-gram session state if not exists
    if 'shared_ngram' not in st.session_state:
        st.session_state.shared_ngram = ""
        
    # Initialize ngram_input_key if not exists
    if 'ngram_input_key' not in st.session_state:
        st.session_state.ngram_input_key = 0
    
    # Load data
    try:
        with st.spinner("Loading data..."):
            df = load_data(path=NGRAM_DATASET_PATH)
            
            # Validate that we have data
            if df is None or df.empty:
                st.error("Failed to load data. Please check your data source.")
                st.stop()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()
    
    # Create navbar and get selected page
    selected_page = create_navbar()
    
    # Render the consistent n-gram input component
    validated_ngram = render_ngram_input(df)
    
    # Render the selected page
    # if selected_page == "General Overview":
    #     render_overview(df)
    if selected_page == "Criteria Functions":
        render_criteria_functions(df)
    elif selected_page == "Trend Detection":
        render_trend_detection(df)
    
if __name__ == "__main__":
    # Create required directories
    for dir_path in ["cache"]:
        os.makedirs(dir_path, exist_ok=True)
    
    main()