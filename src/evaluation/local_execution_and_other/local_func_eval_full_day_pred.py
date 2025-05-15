import os
import pandas as pd
import unicodedata
from sklearn.metrics import (
    root_mean_squared_error,
    mean_absolute_error,
    r2_score
)

# Define static local paths
REAL_CONS_PATH = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\data\s3_downloaded_datasets\real_cons_data.csv"
LOCAL_BASE_DIR = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Predictions_archive"

def evaluate_full_day_prediction(region, region_abbr_caps, region_abbr_lwrc, target_month, chosen_day, run_time_hr):
    """
    Evaluates the full-day prediction file (ALL_MODELS) for a given run_time (local version).
    Saves merged eval file and appends metrics to the same metrics file.
    """

    date_str = chosen_day.strftime("%Y-%m-%d")

    # 🔧 Construct run_time_path internally
    run_time_path = os.path.join(
        LOCAL_BASE_DIR,
        region_abbr_caps,
        target_month,
        date_str,
        str(run_time_hr)
    )

    pred_filename = f"pred_full_{region_abbr_lwrc}_{date_str}_{run_time_hr}.csv"
    pred_path = os.path.join(run_time_path, "pred", pred_filename)

    if not os.path.exists(pred_path):
        print(f"⚠️ Full-day prediction file not found: {pred_path}")
        return

    df_pred = pd.read_csv(pred_path)
    df_pred["Datetime"] = pd.to_datetime(df_pred["Datetime"])
    df_pred.rename(columns={"Predicted_Consumption": "y_pred"}, inplace=True)

    # Load and filter real data
    df_real = pd.read_csv(REAL_CONS_PATH)
    df_real["Datetime"] = pd.to_datetime(df_real["Datetime"])

    normalized_region = unicodedata.normalize("NFKD", region)
    df_real = df_real[df_real["Région"].apply(lambda x: unicodedata.normalize("NFKD", x)) == normalized_region].copy()
    df_real.rename(columns={"Consommation (MW)": "y_real"}, inplace=True)

    df_real_day = df_real[df_real["Datetime"].dt.date == chosen_day.date()].copy()

    if df_real_day.empty:
        print(f"⚠️ No real data found for full-day evaluation on {date_str}.")
        return

    df_eval = pd.merge(df_pred, df_real_day, on="Datetime", suffixes=("_pred", "_real"))

    # Compute metrics
    mae = mean_absolute_error(df_eval["y_real"], df_eval["y_pred"])
    rmse = root_mean_squared_error(df_eval["y_real"], df_eval["y_pred"])
    r2 = r2_score(df_eval["y_real"], df_eval["y_pred"])
    mean_consumption = df_eval["y_real"].mean()

    metrics = [{
        "Model": "ALL_MODELS",
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
        "MAE / Mean": mae / mean_consumption,
        "RMSE / Mean": rmse / mean_consumption
    }]

    # Save evaluation CSV
    eval_folder = os.path.join(run_time_path, "eval")
    os.makedirs(eval_folder, exist_ok=True)

    eval_filename = f"eval_full_{region_abbr_lwrc}_{date_str}_{run_time_hr}.csv"
    eval_path = os.path.join(eval_folder, eval_filename)
    df_eval.to_csv(eval_path, index=False)
    print(f"✅ Full-day evaluation saved: {eval_path}")

    # Append metrics to the existing metrics file
    metrics_df = pd.DataFrame(metrics)
    metrics_filename = f"metrics_individual_models_{region_abbr_lwrc}_{date_str}_{run_time_hr}.csv"
    metrics_path = os.path.join(eval_folder, metrics_filename)

    if os.path.exists(metrics_path):
        try:
            existing_df = pd.read_csv(metrics_path)
            combined_df = pd.concat([existing_df, metrics_df], ignore_index=True)
        except Exception:
            combined_df = metrics_df
    else:
        combined_df = metrics_df

    combined_df.to_csv(metrics_path, index=False)
    print(f"📊 Metrics (ALL_MODELS) appended to: {metrics_path}")
