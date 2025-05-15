# streamlit_src/view/prediction.py

import streamlit as st
import pandas as pd
import plotly.io as pio
from datetime import date, timedelta
from utils.io_s3 import read_json_from_s3

def render_prediction_tab():
    target_day = date.today() + timedelta(days=1)
    fr_date_dmy = target_day.strftime("%d-%m-%Y")

    st.title(f"🔮 Prédiction de Consommation Electrique du {fr_date_dmy}")

    # === REGION SETUP ===
    region_mapping = {
        "Auvergne-Rhône-Alpes": "ARA",
        "Bourgogne-Franche-Comté": "BFC",
        "Bretagne": "BRE",
        "Centre-Val de Loire": "CVL",
        "Grand Est": "GRE",
        "Hauts-de-France": "HDF",
        "Île-de-France": "IDF",
        "Nouvelle-Aquitaine": "NAQ",
        "Occitanie": "OCC",
        "Provence-Alpes-Côte d'Azur": "PAC",
        "Pays de la Loire": "PAL",        
    }

    region = st.selectbox("Sélectionner la région", sorted(region_mapping.keys()), index=0)
    region_abbr = region_mapping[region]
    region_abbr_lwrc = region_abbr.lower()
    
    # === RUN TIME SELECTION ===
    available_run_times = [2, 8, 14, 20]
    default_run_time = max(available_run_times)
    run_time_hr = st.selectbox("Sélectionner l'heure de prédiction", available_run_times, index=available_run_times.index(default_run_time))

    # === DATE SETUP ===
    date_ymd = target_day.strftime("%Y-%m-%d")
    target_month = target_day.strftime("%Y-%m")

    # === S3 PATH ===
    run_time_pred_folder_key = f"Predictions/{region_abbr}/{target_month}/{date_ymd}/{run_time_hr}/pred"
    plot_filename = f"plot_pred_full_{region_abbr_lwrc}_{date_ymd}_{run_time_hr}.json"
    plot_key = f"{run_time_pred_folder_key}/{plot_filename}"

    st.caption(f"Chargement du graphique depuis: '{plot_key}'")

    data = read_json_from_s3(plot_key)

    if not data:
        st.error("⚠️ Impossible de charger le fichier de prédiction.")
        return
    
    try:
        fig = pio.from_json(data)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"⚠️ Échec de l'affichage du graphique: {e}")
