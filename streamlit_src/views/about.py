import streamlit as st

def render_about_tab():
    st.title("🌐 À propos")

    tabs = st.tabs(["🇫🇷 Français", "🇬🇧 English"])

    with tabs[0]:  # Français
        st.markdown("""
### Présentation
Cette application affiche des prédictions de consommation électrique régionale en France à l’horizon D+1. Elle combine modélisation statistique, automatisation cloud et visualisation interactive.

### Objectifs du projet
- Construire un pipeline automatisé de prédiction de la consommation régionale
- Mettre en œuvre des modèles XGBoost supervisés et les évaluer sur données réelles
- Proposer une interface publique et pédagogique basée sur Streamlit

### Approche technique
- Modèles entraînés avec MLflow (XGBoost)
- Orchestration via AWS: S3, ECS, EventBridge
- Visualisation avec Plotly et Streamlit
- Stockage des prévisions et évaluations au format JSON et CSV

### À propos de l’auteur
Je suis biologiste de formation, spécialisé en microbiologie des sols. Je me suis formé à la data science pour mieux comprendre, modéliser et déployer des systèmes complexes. Ce projet a été réalisé dans le cadre de ma certification RNCP et pour enrichir mon portfolio professionnel.
GitHub : https://github.com/HenriSandifer/Predi_Conso_Elec_Region
                    """)

    with tabs[1]:  # English
        st.markdown("""
### Overview
This app presents next-day electricity consumption forecasts for French regions. It combines statistical modeling, cloud automation, and interactive visualization.

### Project Objectives
- Build an end-to-end pipeline for regional electricity forecasting
- Implement and evaluate XGBoost models on public data
- Offer a public-facing and educational interface with Streamlit

### Technical Approach
- Models trained and versioned using MLflow (XGBoost)
- AWS-based orchestration: S3, ECS, EventBridge
- Visuals built with Plotly and rendered in Streamlit
- Forecasts and evaluations stored in JSON and CSV formats

### About the Author
I’m a biologist with a specialization in soil microbiology. I transitioned into data science to explore, model, and deploy real-world systems. This project was developed for my RNCP certification and to showcase my full-stack data skills.
GitHub : https://github.com/HenriSandifer/Predi_Conso_Elec_Region
                    """)
