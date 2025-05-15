# app.py
import streamlit as st
from router import render_tabs
import os


# Optional: Set Streamlit page config
st.set_page_config(
    page_title="ForecastElec | France Regional Predictions",
    page_icon="🌞",  # a sun symbol
    layout="wide"
)

# Optional styling / CSS loader (from assets later)
css_path = "streamlit_src/assets/styles.css"
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Optional future hook for user session
# from models.session import load_user_session
# load_user_session()

# App entrypoint: show tabbed interface
render_tabs()
