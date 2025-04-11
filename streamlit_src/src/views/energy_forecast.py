import streamlit as st
import pandas as pd
import os
import random
import matplotlib.pyplot as plt
from src.views import home, goal, dataset, analysis, conclusion, options, login, logout, energy_forecast
import sys
import os
import utils as utl
from src.router import get_route, redirect
import json
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
utl.inject_custom_css()
utl.navbar_component()

def load_view():
    st.title("⚡ Electricity Consumption Forecast")

    # 📌 Load a random D+1 prediction file from the archive for testing
    past_prediction_files = [f for f in os.listdir(r"C:\Users\Henri\Documents\Data Science Bootcamp\Projet File Rouge\Github PFR\projet-fil-rouge-SE3D-app\Projet\Streamlit\data\past_predictions") if f.startswith("prediction_")]
    if not past_prediction_files:
        st.error("No past prediction files found.")
        st.stop()

    # Select a random file for testing
    random_prediction_file = random.choice(past_prediction_files)
    file_path = os.path.join(r"C:\Users\Henri\Documents\Data Science Bootcamp\Projet File Rouge\Github PFR\projet-fil-rouge-SE3D-app\Projet\Streamlit\data\past_predictions", random_prediction_file)

    # Load the test D+1 prediction
    df_pred = pd.read_csv(file_path, parse_dates=["Datetime"])

    # Filter by the selected region
    df_region_pred = df_pred[df_pred["Région"] == "Occitanie"]

   
    fig = go.Figure()

    # Actual consumption trace
    fig.add_trace(go.Scatter(
        x=df_region_pred["Datetime"],
        y=df_region_pred["Consommation (MW)"],
        mode="lines+markers",
        name="Actual Consumption",
        hovertemplate="Time: %{x}<br>Actual: %{y:.2f} MW<extra></extra>"
    ))

    # Predicted consumption trace with custom data for difference and percentage difference
    fig.add_trace(go.Scatter(
        x=df_region_pred["Datetime"],
        y=df_region_pred["Predicted_Consumption"],
        mode="lines+markers",
        name="Predicted Consumption",
        customdata=np.stack((df_region_pred["Difference"], df_region_pred["Pct_Diff"]), axis=-1),
        hovertemplate=("Time: %{x}<br>Predicted: %{y:.2f} MW"
                   "<br>Difference: %{customdata[0]:.2f} MW"
                   "<br>Delta: %{customdata[1]:.1f}%<extra></extra>")
    ))

    # You can set the hover mode; "closest" is simpler than unified:
    fig.update_layout(hovermode="x unified")
    
    st.plotly_chart(fig)
