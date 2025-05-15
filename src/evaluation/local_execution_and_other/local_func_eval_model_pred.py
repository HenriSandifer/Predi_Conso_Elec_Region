import os
import pandas as pd
import unicodedata
from sklearn.metrics import (
    root_mean_squared_error,
    mean_absolute_error,
    r2_score
)
from dictionaries import run_time_dict
from utils_pred_eval_inputs import get_pred_eval_inputs

# Local paths
REAL_CONS_PATH = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\data\s3_downloaded_datasets\real_cons_data.csv"
LOCAL_BASE_DIR = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Predictions_archive"

def evaluate_model_predictions(region, region_abbr_caps, region_abbr_lwrc, target_month, chosen_day, run_time_hr):
    """
    Evaluates all individual model predictions for a given region/run_time/day (local version).
    Saves evaluation CSVs and metrics to eval folder inside run_time_path.
    """

    date_ymd = chosen_day.strftime("%Y-%m-%d")

    # 🔧 Construct local path automatically
    run_time_path = os.path.join(
        LOCAL_BASE_DIR,
        region_abbr_caps,
        target_month,
        date_ymd,
        str(run_time_hr)
    )

    # Set folder paths
    pred_folder = os.path.join(run_time_path, "pred")
    eval_folder = os.path.join(run_time_path, "eval")
    os.makedirs(eval_folder, exist_ok=True)

    if not os.path.exists(pred_folder):
        print(f"⚠️ No pred folder found at: {pred_folder}")
        return

    # Only consider individual model predictions
    pred_files = [
        f for f in os.listdir(pred_folder)
        if f.startswith("pred_cons_") and f.endswith(".csv")
    ]

    if not pred_files:
        print(f"⚠️ No individual prediction files found in {pred_folder}")
        return

    # Load real consumption data
    df_real = pd.read_csv(REAL_CONS_PATH)
    df_real["Datetime"] = pd.to_datetime(df_real["Datetime"])
    normalized_region = unicodedata.normalize("NFKD", region)
    df_real = df_real[df_real["Région"].apply(lambda x: unicodedata.normalize("NFKD", x)) == normalized_region].copy()
    df_real.rename(columns={"Consommation (MW)": "y_real"}, inplace=True)

    metrics = []

    for filename in pred_files:
        try:
            parts = filename.split("_")
            model_name = parts[3]
        except IndexError:
            print(f"⚠️ Could not parse model name from filename: {filename}")
            continue

        pred_path = os.path.join(pred_folder, filename)
        df_pred = pd.read_csv(pred_path)
        df_pred["Datetime"] = pd.to_datetime(df_pred["Datetime"])
        df_pred.rename(columns={"Predicted_Consumption": "y_pred"}, inplace=True)

        # Get evaluation window
        normalized_run_time = f"{int(run_time_hr):02d}:00:00"
        inputs = get_pred_eval_inputs(region, chosen_day.strftime("%Y-%m-%d"), model_name.upper(), normalized_run_time)
        start = inputs["first_row"]
        end = inputs["last_row"]

        df_real_window = df_real[(df_real["Datetime"] >= start) & (df_real["Datetime"] <= end)].copy()

        if df_real_window.empty:
            print(f"⚠️ No real data found for {model_name.upper()} timeframe.")
            continue

        df_eval = pd.merge(df_pred, df_real_window, on="Datetime", suffixes=("_pred", "_real"))

        # Compute metrics
        mae = mean_absolute_error(df_eval["y_real"], df_eval["y_pred"])
        rmse = root_mean_squared_error(df_eval["y_real"], df_eval["y_pred"])
        r2 = r2_score(df_eval["y_real"], df_eval["y_pred"])
        mean_consumption = df_eval["y_real"].mean()

        metrics.append({
            "Model": model_name.upper(),
            "MAE": mae,
            "RMSE": rmse,
            "R2": r2,
            "MAE / Mean": mae / mean_consumption,
            "RMSE / Mean": rmse / mean_consumption
        })

        # Save evaluation file
        eval_filename = f"eval_{region_abbr_lwrc}_{model_name}_{date_ymd}_{run_time_hr}.csv"
        eval_path = os.path.join(eval_folder, eval_filename)
        df_eval.to_csv(eval_path, index=False)
        print(f"✅ Evaluation saved: {eval_path}")

    if metrics:
        metrics_df = pd.DataFrame(metrics)
        metrics_filename = f"metrics_individual_models_{region_abbr_lwrc}_{date_ymd}_{run_time_hr}.csv"
        metrics_path = os.path.join(eval_folder, metrics_filename)
        metrics_df.to_csv(metrics_path, index=False)
        print(f"📊 Metrics summary saved: {metrics_path}")
