import streamlit as st

def create_navbar():
    """
    Creates a navigation bar with buttons for page selection.
    Uses different button types to indicate the active page.
    
    Returns:
        str: The selected page name
    """
    # Initialize session state for page selection if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Criteria Functions"
    
    # Create columns for the buttons
    col1, col2, col3, = st.columns([1, 1, 3])
    
    # # General Overview button - primary if active, secondary if not
    # with col1:
    #     if st.button(
    #         "General Overview", 
    #         key="btn_overview", 
    #         use_container_width=True,
    #         type="primary" if st.session_state.current_page == "General Overview" else "secondary"
    #     ):
    #         st.session_state.current_page = "General Overview"
    #         st.rerun()
    
    # N-gram Analysis button - primary if active, secondary if not
    with col1:
        if st.button(
            "Criteria Functions", 
            key="btn_ngram_analysis", 
            use_container_width=True,
            type="primary" if st.session_state.current_page == "Criteria Functions" else "secondary"
        ):
            st.session_state.current_page = "Criteria Functions"
            st.rerun()
    
    # Trend Intervals button - primary if active, secondary if not
    with col2:
        if st.button(
            "Trend Detection", 
            key="btn_trend_detection", 
            use_container_width=True,
            type="primary" if st.session_state.current_page == "Trend Detection" else "secondary"
        ):
            st.session_state.current_page = "Trend Detection"
            st.rerun()
    
    # Return currently selected page
    return st.session_state.current_page