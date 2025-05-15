import streamlit as st
import pandas as pd
import plotly.express as px
from utils.io_s3 import read_csv_from_s3

BUCKET_NAME = "predi-conso-elec-region"
S3_PREFIX = "Predictions/"
months = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05"]

region_map = {
    "ARA": "Auvergne-Rhône-Alpes",
    "OCC": "Occitanie",
    "NAQ": "Nouvelle-Aquitaine",
    "PAC": "Provence-Alpes-Côte d'Azur",
    "HDF": "Hauts-de-France",
    "PAL": "Pays de la Loire",
    "BRE": "Bretagne",
    "GRE": "Grand Est",
    "CVL": "Centre-Val de Loire",
    "BFC": "Bourgogne-Franche-Comté",
    "IDF": "Île-de-France"
}

@st.cache_data
def load_national_metrics():
    df_list = []
    for Month in months:
        key = f"{S3_PREFIX}metrics_master_national_{Month}.csv"
        df = read_csv_from_s3(key)
        if df is not None:
            df["Month"] = Month
            df_list.append(df)
    if not df_list:
        return pd.DataFrame()
    df_all = pd.concat(df_list, ignore_index=True)
    df_all["Date"] = pd.to_datetime(df_all["Date"])
    df_all["Run_time"] = df_all["Run_time"].astype(str)
    return df_all
    

def render_analysis_tab():
    st.title("🔬 Dashboard analytique: Métriques de Prédiction de Consommation Electrique")

    df_all = load_national_metrics()
    if df_all.empty:
        st.warning("Aucune métrique n'a pû être chargée depuis s3.")
        st.stop()

    df_all.rename(columns={"Region": "Régions", "Model": "Modèles", "Run_time": "Heures d'exécution", "Month" : "Mois"}, inplace=True)

    # Default display on page load
    grouped = df_all.groupby(["Régions", "Heures d'exécution", "Modèles", "Mois"]).agg({
        "MAE": "mean",
        "RMSE": "mean",
        "R2": "mean",
        "MAE / Mean": "mean",
        "RMSE / Mean": "mean"
    }).reset_index()


    df_all_models = grouped[grouped["Modèles"] == "ALL_MODELS"]
    df_all_models["Régions"] = df_all_models["Régions"].map(region_map)
    df_avg_by_region = df_all_models.groupby(["Régions"]).agg({"R2": "mean"}).reset_index()
    fig_default = px.bar(
        df_avg_by_region,
        x="Régions",
        y="R2",
        color="Régions",
        title="Valeur R² moyenne de tous les modèles par région pour 2025"
    )
    fig_default.update_layout(xaxis_type="category", showlegend=False)
    st.plotly_chart(fig_default, use_container_width=True)

    # Other info
    st.markdown("---")
    st.markdown("### Informations")
    st.markdown("__*R2 :__ Coefficient de Détermination : plus le coefficient de détermination " \
    "est proche de 1, plus le modèle est en adéquation avec les données collectées et plus la" \
    " régression est efficace pour prédire les résultats futurs ")

    # Filter UI should only appear on analysis tab
    st.markdown("---")
    st.markdown("### Filtres")
    st.markdown("Graphique intéractif en bas de page")

    all_Région = sorted(df_all["Régions"].unique())
    with st.expander("# 📘 Légende des abbréviations des régions :"):
        st.markdown("""
        | Abbréviation | Région                     |
        |--------------|----------------------------|
        | ARA          | Auvergne-Rhône-Alpes       |
        | BFC          | Bourgogne-Franche-Comté    |
        | BRE          | Bretagne                   |
        | CVL          | Centre-Val de Loire        |
        | GRE          | Grand Est                  |
        | HDF          | Hauts-de-France            |
        | IDF          | Île-de-France              |
        | NAQ          | Nouvelle-Aquitaine         |
        | OCC          | Occitanie                  |
        | PAC          | Provence-Alpes-Côte d'Azur |
        | PAL          | Pays de la Loire           |
        """)

    all_mois = sorted(df_all["Mois"].unique())
    all_models = sorted(df_all["Modèles"].unique())
    all_runtimes = sorted(df_all["Heures d'exécution"].unique())

    def default_models():
        return ["ALL_MODELS"] if "ALL_MODELS" in all_models else all_models

    Région = st.multiselect("Régions", all_Région, default=all_Région)
    mois = st.multiselect("Mois", all_mois, default=all_mois)
    models = st.multiselect("Modèles", all_models, default=default_models())
    runtimes = st.multiselect("Heures d'exécution", all_runtimes, default=all_runtimes)

    group_by = st.selectbox("Regrouper par (axe X)", ["Régions", "Mois", "Modèles", "Heures d'exécution"])
    chart_type = st.selectbox("Type de graphique", ["Ligne", "Barre", "Boîte à moustaches"])

    # Filtered view
    df_filtered = df_all[
        df_all["Régions"].isin(Région) &
        df_all["Mois"].isin(mois) &
        df_all["Modèles"].isin(models) &
        df_all["Heures d'exécution"].isin(runtimes) &
        (df_all["R2"] > -1)
    ]

    if df_filtered.empty:
        st.warning("No data for selected filters.")
        st.stop()

    group_keys = [group_by] if group_by == "Régions" else [group_by, "Régions"]
    df_grouped = df_filtered.groupby(group_keys)["R2"].mean().reset_index()
    df_grouped["Régions"] = df_grouped["Régions"].map(region_map)

    # Plot
    if chart_type == "Ligne":
        fig = px.line(df_grouped, x=group_by, y="R2", color="Régions", markers=True)
    elif chart_type == "Barre":
        fig = px.bar(df_grouped, x=group_by, y="R2", color="Régions", text_auto=".2f")
    elif chart_type == "Boîte à moustaches":
        fig = px.box(df_filtered, x=group_by, y="R2", color=group_by)

    fig.update_layout(title=f"R² regroupé par {group_by}", yaxis_title="R²", xaxis_type="category")
    st.plotly_chart(fig, use_container_width=True)
