import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_data(path):
    try:
        if (os.path.exists(path)):
            df = pd.read_pickle(path)
            # odrezemo prve 4 quartile, ker so prazni
            df = df.iloc[:, 4:]
            return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None