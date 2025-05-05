# views/evaluation.py

import streamlit as st
import plotly.io as pio
import json

def render_evaluation_tab():
    st.header("📈 Evaluation of Yesterday's Prediction")

    st.markdown("Visual comparison between prediction and actual consumption.")

    # Placeholder: dropdowns (same as prediction)
    region = st.selectbox("Select Region", ["Occitanie", "Nouvelle-Aquitaine", "Île-de-France"])
    day = st.date_input("Choose Day to Evaluate")

    # Placeholder: load evaluation JSON
    try:
        with open("sample_data/evaluation_sample.json", "r") as f:
            fig_dict = json.load(f)
        fig = pio.from_json(json.dumps(fig_dict))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not load evaluation plot: {e}")
