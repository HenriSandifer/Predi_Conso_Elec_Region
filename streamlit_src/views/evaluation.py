# views/evaluation.py

import streamlit as st
import plotly.io as pio
import plotly.graph_objects as go
from datetime import date, timedelta
from utils.io_s3 import read_json_from_s3, read_csv_from_s3
import pandas as pd

def render_evaluation_tab():
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

    region = st.selectbox("Sélectionner la région", sorted(region_mapping.keys()), index=0, key="eval_region_select")
    region_abbr = region_mapping[region]
    region_abbr_lwrc = region_abbr.lower()

    target_day = date.today() - timedelta(days=1)

    # === DATE SELECTION ===
    selected_date = st.date_input("Sélectionner la date (J-1)", target_day, key="eval_date_input")
    date_ymd = selected_date.strftime("%Y-%m-%d")
    target_month = selected_date.strftime("%Y-%m")
    
    fr_date_dmy = selected_date.strftime("%d-%m-%Y")

    # === RUN TIME ===
    available_run_times = [2, 8, 14, 20]
    default_run_time = max(available_run_times)
    run_time_hr = st.selectbox("Sélectionner l'heure de prédiction", available_run_times, index=available_run_times.index(default_run_time), key="eval_run_time_select")

    st.title(f"📊 Évaluation de la Prédiction (J-1) de Consommation Electrique du {fr_date_dmy}")

    # === S3 PATH ===
    run_time_eval_folder_key = f"Predictions/{region_abbr}/{target_month}/{date_ymd}/{run_time_hr}/eval"
    plot_filename = f"plot_eval_full_{region_abbr_lwrc}_{date_ymd}_{run_time_hr}.json"
    plot_key = f"{run_time_eval_folder_key}/{plot_filename}"

    st.caption(f"Chargement du graphique depuis : '{plot_key}")

    data = read_json_from_s3(plot_key)

    # === Load R² from metrics CSV ===
    metrics_filename = f"metrics_individual_models_{region_abbr_lwrc}_{date_ymd}_{run_time_hr}.csv"
    metrics_key = f"{run_time_eval_folder_key}/{metrics_filename}"
    metrics_df = read_csv_from_s3(metrics_key)

    r2_score = None
    if metrics_df is not None and not metrics_df.empty:
        df = pd.DataFrame(metrics_df)
        if "Model" in df.columns and "R2" in df.columns:
            df_all_models = df[df["Model"] == "ALL_MODELS"]
            if not df_all_models.empty:
                r2_score = df_all_models.iloc[0]["R2"]

    # === Display R² before chart ===
    if r2_score is not None:
        st.markdown(f"### R² : `{r2_score:.4f}`")
    else:
        st.warning("R² introuvable pour ALL_MODELS dans les métriques.")


    if not data:
        st.error("⚠️ Impossible de charger le fichier d'évaluation.")
        return
    
    try:
        fig = pio.from_json(data)
        if len(fig.data) == 2 and fig.data[0].name == "Real Consumption":
            fig.data = (fig.data[1], fig.data[0])
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Échec de l'affichage du graphique : {e}")