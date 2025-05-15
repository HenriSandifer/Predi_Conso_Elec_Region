# router.py

import streamlit as st
from views.prediction import render_prediction_tab
from views.evaluation import render_evaluation_tab
from views.analysis import render_analysis_tab
from views.about import render_about_tab

def render_tabs():
    tabs = st.tabs(["🔮 Prediction", "📈 Evaluation", "🔬 Analyse", "🌐 A propos"])

    with tabs[0]:
        render_prediction_tab()

    with tabs[1]:
        render_evaluation_tab()

    with tabs[2]:
        render_analysis_tab()

    with tabs[3]:
        render_about_tab()