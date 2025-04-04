import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
import unicodedata
from utils import prepare_pipeline_inputs
from dictionaries import prediction_timeframes


def evaluate_all_predictions(region_abbr_caps, region_abbr_lwrc, chosen_day, run_time_str, func_region):
    date_str = chosen_day.strftime("%Y-%m-%d")
    base_dir = "Predictions"
    run_time_folder = os.path.join(base_dir, region_abbr_caps, date_str, str(run_time_str))

    # Gather CSV files
    prediction_files = [
        os.path.join(run_time_folder, f)
        for f in os.listdir(run_time_folder)
        if f.endswith(".csv") and "all_models" not in f  # Avoid reloading concatenated full-day prediction
    ]

    if not prediction_files:
        print("\u26a0\ufe0f No prediction files found for this run time.")
        return

    df_real = pd.read_csv(
        r"C:\\Users\\Henri\\Documents\\GitHub\\Predi_Conso_Elec_Region\\Predi_Conso_Elec_Region\\data\\cons_temp_2025.csv",
        parse_dates=['Datetime']
    )
    normalized_region = unicodedata.normalize("NFKD", func_region)
    df_real = df_real[
        (df_real["Région"].apply(lambda x: unicodedata.normalize("NFKD", x)) == normalized_region)
    ].copy()
    df_real.rename(columns={"Consommation (MW)": "y_real"}, inplace=True)

    metrics = []
    full_day_df = []

    for file in prediction_files:
        df_pred = pd.read_csv(file, parse_dates=["Datetime"])
        model_name = [part for part in file.split("_") if part.startswith("m")][0]  # e.g., "m18"

        # Prepare model-specific time window
        inputs = prepare_pipeline_inputs(func_region, chosen_day.strftime("%Y-%m-%d"), model_name.upper(), run_time_str)
        start = inputs["first_row"]
        end = inputs["last_row"]

        # Filter real
        df_real_window = df_real[(df_real['Datetime'] >= start) & (df_real['Datetime'] <= end)].copy()

        if df_real_window.empty:
            print(f"\u26a0\ufe0f No real data found for {model_name.upper()} timeframe.")
            continue

        df_pred.rename(columns={"Predicted_Consumption": "y_pred"}, inplace=True)
        df_eval = pd.merge(df_pred, df_real_window, on="Datetime", suffixes=("_pred", "_real"))

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

        full_day_df.append(df_pred)

    # Full day concatenation
    df_pred_full = pd.concat(full_day_df).sort_values("Datetime")
    df_real_day = df_real[df_real['Datetime'].dt.date == chosen_day.date()].copy()
    df_eval_full = pd.merge(df_pred_full, df_real_day, on="Datetime")

    mae = mean_absolute_error(df_eval_full["y_real"], df_eval_full["y_pred"])
    rmse = root_mean_squared_error(df_eval_full["y_real"], df_eval_full["y_pred"])
    r2 = r2_score(df_eval_full["y_real"], df_eval_full["y_pred"])
    mean_consumption = df_eval_full["y_real"].mean()

    metrics.append({
        "Model": "ALL_MODELS",
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
        "MAE / Mean": mae / mean_consumption,
        "RMSE / Mean": rmse / mean_consumption
    })

    # Save metrics
    metrics_df = pd.DataFrame(metrics)
    metrics_path = os.path.join(run_time_folder, f"evaluation_metrics_{region_abbr_lwrc}_{run_time_str}.csv")
    metrics_df.to_csv(metrics_path, index=False)
    print(f"\ud83d\udcca Metrics saved to: {metrics_path}")

    # Plot full-day only
    plt.figure(figsize=(12, 5))
    plt.plot(df_eval_full["Datetime"], df_eval_full["y_real"], label="Real", linewidth=2)
    plt.plot(df_eval_full["Datetime"], df_eval_full["y_pred"], label="Predicted", linestyle="--")
    plt.title(f"{region_abbr_caps} - {chosen_day} - {run_time_str} D0 Run\nPredicted vs Real Consumption")
    plt.xlabel("Time")
    plt.ylabel("MW")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(run_time_folder, f"prediction_plot_{region_abbr_lwrc}_{run_time_str}.png")
    plt.savefig(plot_path)
    print(f"\ud83d\udcc8 Plot saved to: {plot_path}")
