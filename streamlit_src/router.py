# router.py

import streamlit as st
from views.prediction import render_prediction_tab
from views.evaluation import render_evaluation_tab

def render_tabs():
    tabs = st.tabs(["🔮 Prediction", "📈 Evaluation"])

    with tabs[0]:
        render_prediction_tab()

    with tabs[1]:
        render_evaluation_tab()
