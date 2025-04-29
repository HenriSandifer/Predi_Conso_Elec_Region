import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.preprocessing import PolynomialFeatures
from dictionaries import (lag_roll_features_by_model,
                          run_time_temp_column_map,
                          temp_column_priority)
import mlflow
import unicodedata


from utils_s3 import read_csv_from_s3, write_csv_to_s3

from utils_preprocessing import (add_holiday_column,
                   apply_lag_roll_features,
                   create_prediction_output_key)

from utils_df_test_inputs import get_df_test_inputs

S3_TEMP_FILENAME = "raw_data/temperature_forecast_data.csv"
S3_CONS_FILENAME = "raw_data/real_cons_data.csv"

def run_pipeline_for_model(region, chosen_day, run_time_hr, model):
    # Use your existing prep function
    inputs = get_df_test_inputs(region, chosen_day, model, run_time_hr)

    s3_folder_key = create_prediction_output_key(
    region_abbr_caps=inputs["region_caps"],
    target_month=inputs["chosen_day"].strftime("%Y-%m"),
    chosen_day=inputs["chosen_day"],
    run_time_hr=inputs["run_time_abbr"]
    )

    region_lwrc = inputs["region_abbr"]                        
    date_str = inputs["chosen_day"].strftime("%m-%d")
    run_time_hr = str(inputs["run_time_abbr"])
    model = inputs["model"]

    # From here on, everything that was in your notebook — reading data, feature engineering, model loading...
    print(f"✅ Running pipeline for {region} on {chosen_day} at {run_time_hr} using model {model}")
    
    # Example: run ML pipeline steps (preprocessing, inference, saving output)
    # df_test = build_test_set(inputs)
    # xgb_model = load_model(inputs) 
    # predictions = xgb_model.predict(...)
    # Save predictions to CSV
    # Evaluate and log metrics with MLflow

    # Defining df_cons
    df_cons = read_csv_from_s3(S3_CONS_FILENAME)

    # Normalize Région column
    df_cons["Région"] = df_cons["Région"].apply(lambda x: unicodedata.normalize("NFC", x))
    df_cons = df_cons[df_cons["Région"] == region].copy()
    
    # FEATURE ENGINEERING WITH TIME MARKERS
    df_cons['DayOfWeek'] = df_cons['Datetime'].dt.weekday
    df_cons['IsWeekend'] = df_cons['DayOfWeek'].isin([5, 6])  # Saturday and Sunday are weekend
    df_cons['HourOfDay'] = df_cons['Datetime'].dt.hour

    df_cons['IsMorning'] = df_cons['HourOfDay'].between(6, 11)
    df_cons['IsAfternoon'] = df_cons['HourOfDay'].between(12, 17)
    df_cons['IsEvening'] = df_cons['HourOfDay'].between(18, 22)
    df_cons['IsNight'] = (df_cons['HourOfDay'] >= 23) | (df_cons['HourOfDay'] <= 5)

    df_cons["Month"] = df_cons["Datetime"].dt.month
    df_cons["week_of_year"] = df_cons["Datetime"].dt.isocalendar().week.astype(float)

    # Annual Seasonality
    df_cons["day_of_year"] = df_cons["Datetime"].dt.dayofyear
    df_cons["sin_annual"] = np.sin(2 * np.pi * df_cons["day_of_year"] / 365.25)
    df_cons["cos_annual"] = np.cos(2 * np.pi * df_cons["day_of_year"] / 365.25)

    # Weekly Seasonality
    df_cons["sin_weekly"] = np.sin(2 * np.pi * df_cons["week_of_year"] / 52)
    df_cons["cos_weekly"] = np.cos(2 * np.pi * df_cons["week_of_year"] / 52)
      
    # Daily Seasonality
    df_cons["sin_daily"] = np.sin(2 * np.pi * df_cons["HourOfDay"] / 24)
    df_cons["cos_daily"] = np.cos(2 * np.pi * df_cons["HourOfDay"] / 24)

    # Monthly seasonality
    df_cons["sin_season"] = np.sin(2 * np.pi * df_cons["Month"] / 12)
    df_cons["cos_season"] = np.cos(2 * np.pi * df_cons["Month"] / 12)

    df_cons.drop(columns=['day_of_year', 'week_of_year'], inplace=True)

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

    # Defining df_temp
    df_temp = read_csv_from_s3(S3_TEMP_FILENAME)

    # Normalize Région column
    df_temp["Région"] = df_temp["Région"].apply(lambda x: unicodedata.normalize("NFC", x))
    df_temp = df_temp[df_temp["Région"] == region].copy()

    df_temp = df_temp[
        (df_temp['Datetime'].dt.year == inputs["chosen_day"].year) &
        (df_temp['Datetime'].dt.month.isin([m for m,d in temp_dates])) &
        (df_temp['Datetime'].dt.day.isin([d for m,d in temp_dates]))
    ].copy()

    # Get fallback priority list
    fallback_cols = temp_column_priority.get(run_time_hr)
    if not fallback_cols:
        raise ValueError(f"❌ No temperature columns configured for run_time: {run_time_hr}")
    
    # Get only the D+1 data
    df_temp_day = df_temp[df_temp["Datetime"].dt.day == inputs["chosen_day"].day].copy()
    print(f"df_temp_day len is : {len(df_temp_day)}")
    print(f"df_temp_day looks like : {df_temp_day.describe}")
    
    # Try columns in order
    selected_temp_col = None
    for col in fallback_cols:
        if col in df_temp_day.columns and not df_temp_day[col].isna().any():
            selected_temp_col = col
            break
        elif col in df_temp_day.columns:
            print(f"🕳️ Found NaNs in {col}, checking next fallback...")

    if selected_temp_col is None:
        raise ValueError(f"❌ All fallback temperature columns contain NaNs for {date_str}")
    
    # Final dataframe
    df_t_pred = df_temp_day[["Datetime", selected_temp_col]].copy()
    print(f"df_t_pred len is : {len(df_t_pred)}")
    print(f"df_t_pred looks like : {df_t_pred.describe}")
    df_t_pred.rename(columns={selected_temp_col: "t"}, inplace=True)

    print(f"✅ Using temperature data from column: {selected_temp_col}")

    # Add the Holiday column
    df_test = add_holiday_column(df_test, df_cons) # 

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
    print(f"df_test before adding lag_roll_features is : {len(df_test)}")
    df_test = apply_lag_roll_features(df_test, df_cons, inputs)
    print(f"df_test after adding lag_roll_features is : {len(df_test)}")

    # Apply PolynomialFeatures to interaction features (excluding lag/rolling)
    poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)

    # Prepare D+1 test data in the same way
    X_mixed_test = df_test[all_features]
    nan_cells = [(idx, col) for idx, row in X_mixed_test.iterrows() for col in row.index if pd.isna(row[col])]
    print("🔍 NaNs detected at the following (timestamp, column) locations:")
    for timestamp, col in nan_cells:
        print(f"  → {timestamp} × {col}")
    X_mixed_interactions_test = poly.fit_transform(X_mixed_test)

    X_mixed_interactions_test_df = pd.DataFrame(
        X_mixed_interactions_test,
        columns=poly.get_feature_names_out(input_features=all_features),
        index=X_mixed_test.index
    )

    mlflow.set_tracking_uri("s3://predi-conso-elec-region")
    
    model_version = "1"
    model_name = f"xgb_model_{region_lwrc}_{model.lower()}_v{model_version}"
    model_s3_path = f"s3://predi-conso-elec-region/models/{model_name}"
    
    xgb_model = mlflow.xgboost.load_model(model_s3_path)

    ##### Running Prediction
    # Use the model to predict D+1 consumption
    df_test["Predicted_Consumption"] = xgb_model.predict(X_mixed_interactions_test_df)

    # Save results
    filename = f"pred_cons_{region_lwrc}_{model}_{run_time_hr}_{date_str}_v{model_version}.csv"
    s3_key = f"{s3_folder_key}/{filename}"
    write_csv_to_s3(df_test, s3_key)
    print(f"✅ Added single model prediction for {region_lwrc} run_time {run_time_hr} on {chosen_day} to S3.")
