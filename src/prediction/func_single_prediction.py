import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.preprocessing import PolynomialFeatures
from utils.dictionaries import lag_roll_features_by_model
import os
import mlflow

from src.prediction.utils_preprocessing import (add_holiday_column,
                   apply_lag_roll_features,
                   create_prediction_output_folder,
)

from utils_df_test_inputs import get_df_test_inputs


def run_pipeline_for_model(region, chosen_day, run_time, model):
    # Use your existing prep function
    inputs = get_df_test_inputs(region, chosen_day, model, run_time)

    output_folder = create_prediction_output_folder(
    region_abbr_caps=inputs["region_caps"],
    target_month=inputs["chosen_day"].strftime("%Y-%m"),
    chosen_day=inputs["chosen_day"],
    run_time_str=inputs["run_time_abbr"]
    )

    region_lwrc = inputs["region_abbr"]                          
    date_str = inputs["chosen_day"].strftime("%m-%d")
    run_time = inputs["run_time_abbr"]
    model = inputs["model"]

    # From here on, everything that was in your notebook — reading data, feature engineering, model loading...
    print(f"✅ Running pipeline for {region} on {chosen_day} at {run_time} using model {model}")
    
    # Example: run ML pipeline steps (preprocessing, inference, saving output)
    # df_test = build_test_set(inputs)
    # xgb_model = load_model(inputs) 
    # predictions = xgb_model.predict(...)
    # Save predictions to CSV
    # Evaluate and log metrics with MLflow

    cons_temp_df = pd.read_csv(r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\data\cons_temp_2025.csv", parse_dates=['Datetime'])

    import unicodedata

    # Normalize Région column
    cons_temp_df["Région"] = cons_temp_df["Région"].apply(lambda x: unicodedata.normalize("NFC", x))
    cons_temp_df = cons_temp_df[cons_temp_df["Région"] == region].copy()
    # Define frequency (seasonality)
    cons_temp_df["day_of_year"] = cons_temp_df["Datetime"].dt.dayofyear
    cons_temp_df["week_of_year"] = cons_temp_df["Datetime"].dt.isocalendar().week.astype(float)

    # Annual Seasonality
    cons_temp_df["sin_annual"] = np.sin(2 * np.pi * cons_temp_df["day_of_year"] / 365.25)
    cons_temp_df["cos_annual"] = np.cos(2 * np.pi * cons_temp_df["day_of_year"] / 365.25)

    # Weekly Seasonality
    cons_temp_df["sin_weekly"] = np.sin(2 * np.pi * cons_temp_df["week_of_year"] / 52)
    cons_temp_df["cos_weekly"] = np.cos(2 * np.pi * cons_temp_df["week_of_year"] / 52)

    # Daily Seasonality
    cons_temp_df["sin_daily"] = np.sin(2 * np.pi * cons_temp_df["HourOfDay"] / 24)
    cons_temp_df["cos_daily"] = np.cos(2 * np.pi * cons_temp_df["HourOfDay"] / 24)

    # Monthly seasonality
    cons_temp_df["sin_season"] = np.sin(2 * np.pi * cons_temp_df["Month"] / 12)
    cons_temp_df["cos_season"] = np.cos(2 * np.pi * cons_temp_df["Month"] / 12)

    cons_temp_df.drop(columns=['day_of_year', 'week_of_year'], inplace=True)

    lag_roll_features = lag_roll_features_by_model.get(model, [])

    initial_features = ['t', 'DayOfWeek', 'IsWeekend',
                    'HourOfDay', 'Month', 'WeekOfYear', 'Holiday',
                    'sin_annual', 'cos_annual', 'sin_weekly', 'cos_weekly',
                    'sin_daily', 'cos_daily', 'sin_season', 'cos_season', 'IsMorning',
                    'IsAfternoon', 'IsEvening', 'IsNight']

    all_features = lag_roll_features + initial_features

    # Create empty df_test with only a Datetime column
    df_test = pd.DataFrame({"Datetime": inputs["prediction_timestamps"]})

    df_test["DayOfWeek"] = df_test["Datetime"].dt.weekday
    df_test["IsWeekend"] = df_test["DayOfWeek"].isin([5, 6])  
    df_test["HourOfDay"] = df_test["Datetime"].dt.hour
    df_test["Month"] = df_test["Datetime"].dt.month
    df_test["week_of_year"] = df_test["Datetime"].dt.isocalendar().week.astype(float)

    # Annual Seasonality
    df_test["day_of_year"] = df_test["Datetime"].dt.dayofyear
    df_test["sin_annual"] = np.sin(2 * np.pi * df_test["day_of_year"] / 365.25)
    df_test["cos_annual"] = np.cos(2 * np.pi * df_test["day_of_year"] / 365.25)

    # Weekly Seasonality
    df_test["sin_weekly"] = np.sin(2 * np.pi * df_test["week_of_year"] / 52)
    df_test["cos_weekly"] = np.cos(2 * np.pi * df_test["week_of_year"] / 52)

    # Daily Seasonality
    df_test["sin_daily"] = np.sin(2 * np.pi * df_test["HourOfDay"] / 24)
    df_test["cos_daily"] = np.cos(2 * np.pi * df_test["HourOfDay"] / 24)

    # Monthly seasonality
    df_test["sin_season"] = np.sin(2 * np.pi * df_test["Month"] / 12)
    df_test["cos_season"] = np.cos(2 * np.pi * df_test["Month"] / 12)

    df_test.drop(columns=['day_of_year', 'week_of_year'], inplace=True)

    # FEATURE ENGINEERING WITH TIME MARKERS
    df_test['IsMorning'] = df_test['HourOfDay'].between(6, 11)
    df_test['IsAfternoon'] = df_test['HourOfDay'].between(12, 17)
    df_test['IsEvening'] = df_test['HourOfDay'].between(18, 22)
    df_test['IsNight'] = (df_test['HourOfDay'] >= 23) | (df_test['HourOfDay'] <= 5)

    # For example, if chosen_day is "2025-02-25", then:
    temp_dates = [(inputs["chosen_day"].month,
                inputs["chosen_day"].day),
                ((inputs["chosen_day"] + timedelta(days=1)).month,
                    (inputs["chosen_day"] + timedelta(days=1)).day)]

    df_temp = cons_temp_df[
        (cons_temp_df['Datetime'].dt.year == inputs["chosen_day"].year) &
        (cons_temp_df['Datetime'].dt.month.isin([m for m,d in temp_dates])) &
        (cons_temp_df['Datetime'].dt.day.isin([d for m,d in temp_dates]))
    ].copy()

    # Isolate data of the target day
    df_t_pred = df_temp[df_temp['Datetime'].dt.day == inputs["chosen_day"].day].copy()

    # Add the Holiday column
    df_test = add_holiday_column(df_test, cons_temp_df)

    # Convert to binary (1/0)
    df_test["Holiday"] = df_test["Holiday"].astype(int)

    # Drop the Adjusted column to avoid confusion
    df_test.drop(columns=['Zone'], inplace=True)

    def add_time_features(df):
        return df_test.assign(
            Month=df_test.Datetime.dt.month,
            WeekOfYear=df_test.Datetime.dt.isocalendar().week,
        )

    # Apply to the ENTIRE dataset first
    df_test = add_time_features(df_test)
    df_test = df_test.merge(df_t_pred[["Datetime", "t"]], on="Datetime", how="left")


    df_test = apply_lag_roll_features(df_test, cons_temp_df, inputs)

    # Apply PolynomialFeatures to interaction features (excluding lag/rolling)
    poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)

    # Prepare D+1 test data in the same way
    X_mixed_test = df_test[all_features]
    X_mixed_interactions_test = poly.fit_transform(X_mixed_test)

    X_mixed_interactions_test_df = pd.DataFrame(
        X_mixed_interactions_test,
        columns=poly.get_feature_names_out(input_features=all_features),
        index=X_mixed_test.index
    )
    base_model_dir = "C:/Users/Henri/Documents/GitHub/Predi_Conso_Elec_Region/models"
    
    model_version = "1"
    model_path = os.path.join(base_model_dir, f"xgb_model_{region_lwrc}_{model.lower()}_v1")
    xgb_model = mlflow.xgboost.load_model(model_path)

    ##### Running Prediction
    # Use the model to predict D+1 consumption
    df_test["Predicted_Consumption"] = xgb_model.predict(X_mixed_interactions_test_df)

    # Save results

    csv_path = os.path.join(output_folder, "pred_cons_{}_{}_{}D0_{}_v{}_1.csv".format(region_lwrc, model, run_time, date_str, model_version))
    df_test.to_csv(csv_path, index=False)


