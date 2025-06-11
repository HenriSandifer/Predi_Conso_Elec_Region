# ⚡ Predi Conso Elec Region

[🇫🇷 Lire en français](README.fr.md)

**A predictive web application for French regional electricity consumption**  

Author: [henrisandifer](https://github.com/henrisandifer)

App website : https://predi-elec.onrender.com/

---

## 🔍 Overview

**Predi Conso Elec Region** is a full-stack, end-to-end data science project designed to forecast electricity consumption for all regions in France on a daily basis (D+1). It provides:

- <span style="font-size: 20px;">**Daily predictions** using multiple machine learning models.</span>
&nbsp;

![Dashboard Screenshot](assets/prediction.JPG)

- <span style="font-size: 20px;">**Historical archives** of both real consumption and model predictions.</span></br>
&nbsp;

![Dashboard Screenshot](assets/evaluation.JPG)

- <span style="font-size: 20px;">**Automated model evaluation and visualizations** accessible via a clean web interface.</span></br>
&nbsp;

![Dashboard Screenshot](assets/analytics.JPG)

- A completely automated backend pipeline, deployed and managed in the cloud.

The project was developed as part of my **RNCP Level 6 (Développeur Concepteur d'Applications)** certification and serves as a showcase of my ability to design, deploy, and maintain a real-world data application from scratch.



---

## 🎯 Project Purpose

This project simulates a real-world data science workflow for forecasting electricity demand, a critical task for grid operators and energy providers. It demonstrates:
- Demand prediction under real-time constraints
- Automated ingestion and processing of external data (via APIs)
- Scalable model evaluation and visualization for business insight

---

## 💼 Highlights & Capabilities

This project demonstrates my ability to build and deploy real-world machine learning systems with modern tools and best practices.

### 🔧 Core Features
- **D+1 electricity consumption forecasting** for all French regions
- **Multiple XGBoost models**, each tailored to specific data availability windows
- **Daily ingestion** of temperature and consumption data from public APIs
- **Automated evaluation** of model performance
- **Historical archive** of predictions and evaluations (2025)
- **Interactive Streamlit dashboard** with live forecasts and analytics

### 🛠 Technical Stack & Workflow
- **Python**, **XGBoost**, **Scikit-learn**, **MLFlow** (modeling & versioning)
- **Docker**, **AWS ECS**, **S3**, **EventBridge** (deployment & automation)
- **Pathlib**, **modular job structure**, and dynamic file management
- **Plotly** for interactive graphing
- **Fully containerized** and cloud-native architecture

### 🚀 Project Scope & Ownership
- Built **solo**, end-to-end, as part of my **RNCP Level 6 certification**
- Emphasizes full-stack data science skills, from **feature engineering** to **DevOps**
- Combines **ML, data engineering, backend scripting**, and **dashboard design**

---

## 📐 Codebase Architecture

```bash
root/
├── src/
│   ├── new_data_acquisition/       # 4 modular jobs
│   ├── prediction/
│   ├── evaluation/
│   ├── plotting/


    src/
    └── [job_name]/                # Each job has the same modular structure
        ├── ECS_version/
        ├── local_execution_and_other/
        ├── Dockerfile
        ├── requirements.txt


├── streamlit_src/              # Streamlit app
└── README.md
```

## 🧰 Job-specific Architecture Diagrams (+ Cloud Automation)

- <span style="font-size: 20px;">**"New Data Acquisition"** job architecture</span>
&nbsp;

![New Data Acquisition Diagram](assets/new_data_acquisition_job.png)

- <span style="font-size: 20px;">**"Prediction"** job architecture</span>
&nbsp;

![Prediction Job Diagram](assets/prediction_job.png)

- <span style="font-size: 20px;">**"Evaluation"** job architecture</span>
&nbsp;

![Evaluation Job Diagram](assets/evaluation_job.png)

- <span style="font-size: 20px;">**"Plotting"** job architecture</span>
&nbsp;

![Plotting Job Diagram](assets/plotting_job.png)


## 🧪 Model Design

- **5 XGBoost regression models** for each region, trained and versioned using **MLflow**, with various combinations of models used for each run time (00h, 02h, 08h, 14h).
- Each model was optimized for **specific data availability windows** and **high accuracy**.
- Features include calendar flags (weekday, holidays), weather data (4 forecast time columns), Fourier features (seasonality), lags and rolling averages, and **polynomial interaction terms** for non-linearity.
- Feature selection was performed iteratively using performance metrics on validation sets.
- **Hyperparameter tuning** was conducted via `GridSearchCV` to find optimal combinations (depth, learning rate, number of trees).
- Daily predictions are logged and saved to **AWS S3**, and performance is evaluated against true values the next day (D+1 vs D-1).

---

## 🚀 Installation & Usage

To be able to run or test the project locally (e.g. for prediction):

1. Clone the repo:
   ```bash
   git clone https://github.com/henrisandifer/predi-conso-elec-region.git
   cd predi-conso-elec-region
   ```

2. Navigate to a job folder (e.g., `src/prediction`) and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your AWS credentials (you’ll need access to my S3 buckets to run full workflows).

4. Run a script locally (instructions below)


> ⚠️ Note: Most features are designed to be run in production via Docker + AWS ECS. Local execution is mainly for debugging and testing.

---

## 🗂️ Local vs Cloud Scripts

Each job contains:

- `ECS_version/`: for fully Dockerized cloud deployment (ECS, S3).
- `local_execution_and_other/`: for local script execution. Inside:
  - `local_run_*.py`: main scripts for testing the jobs locally, reading and writing local files.
  - `other_scripts/`: utilities for fixing, inspecting, or preprocessing datasets.

Local paths are dynamically resolved using Python's `pathlib`, so you don't need to modify the code if your project folder is structured correctly.

### 🧪 Running Jobs Locally

### New Data Acquisition job : 
#### To update the local electrical consumption dataset:

```bash
cd src/new_data_acquisition/local_execution_and_other
python local_run_update_cons_data.py
```
#### To update the local temperature forecast datasets:
```bash
cd src/new_data_acquisition/local_execution_and_other
python local_run_update_temperature_forecast.py --run_time “02”
```
### Prediction job :
#### To run a full day prediction for a given region and day at a given run time (make sure the electrical consumption and temperature forecast datasets have the necessary data):
```bash
cd src/prediction/local_execution_and_other
python local_run_all_models_for_time.py --region "Occitanie" --day "2025-04-01" --time "08:00:00"
```
### Evaluation job 
#### To run an evaluation of a prediction for a given region and day
```bash
cd src/evaluation/local_execution_and_other
python run_full_day_eval.py --region “Occitanie” --day “2025-04-01”
```
### Plotting job
#### To plot a given prediction
```bash
cd src/plotting/local_execution_and_other
python run_plot_pred.py --region “Occitanie” --day “2025-04-01” --time “02:00:00”
```
#### To plot a given prediction evaluation
```bash
cd src/plotting/local_execution_and_other
python run_plot_eval.py --region “Occitanie” --day “2025-04-01”
```

---

## 📊 Streamlit Dashboard

The interactive Streamlit UI displays:
- D+1 predictions for the current day for each French region
- Evaluations of each day of 2025 up to date for each French region
- Plots and analytics by model and region

*a lack of data for Normandy excludes it from the app

---

## 🙋 About Me

I'm Henri Sandifer, a former biologist specialized in **soil microbiology and mycorrhizal fungi**, now working in **data science and software engineering**. I've also worked in the **renewable energy sector** and enjoy building real-world apps involving predictive modeling, automation, and cloud deployment.

Languages spoken: **English, French, Italian (fluent)**; **Japanese, Spanish, Arabic, German (intermediate)**.

---

## 📝 License

This project is licensed under the MIT License – see the `LICENSE.md` file for details.
