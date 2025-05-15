import os
import pickle
import streamlit as st
from settings import CACHE_DIR

def get_cache_path(key):
    os.makedirs(CACHE_DIR, exist_ok=True)
    filename = f"{key}.pkl"
    
    return os.path.join(CACHE_DIR, filename)

def get_cached_result(key):
    cache_path = get_cache_path(key)
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            st.warning(f"Error loading cache: {e}")
            return None
    
    return None

def save_cached_result(key, result):
    cache_path = get_cache_path(key)
    
    try:
        with open(cache_path, "wb") as f:
            pickle.dump(result, f)
    except Exception as e:
        st.warning(f"Error saving cache: {e}")