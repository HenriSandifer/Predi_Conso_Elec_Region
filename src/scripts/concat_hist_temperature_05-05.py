import os
import pandas as pd
from datetime import datetime

# Step 1: Merge all regional temp files into a long-format dataframe
def merge_regional_temperature_data(hist_dir, output_path):
    long_dfs = []
    
    for fname in os.listdir(hist_dir):
        if fname.startswith("temp_") and "_hist" in fname:
            fpath = os.path.join(hist_dir, fname)
            try:
                df = pd.read_csv(fpath)
                df["Datetime"] = pd.to_datetime(df["Datetime"])
                
                # Infer region code from filename
                region_abbr = fname.split("_")[1]
                
                # Keep only relevant columns
                df = df[["Datetime", "Région", "t"]]
                
                long_dfs.append(df)
            except Exception as e:
                print(f"❌ Failed to read {fname}: {e}")

    if not long_dfs:
        raise ValueError("No valid temperature files found.")

    df_all = pd.concat(long_dfs)
    df_all.sort_values(["Datetime", "Région"], inplace=True)
    df_all.to_csv(output_path, index=False)
    print(f"✅ Long-format temperature file saved to: {output_path}")
    
    return df_all


if __name__ == "__main__":
    hist_folder = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Pipelines"
    merged_hist_path = os.path.join(hist_folder, "national_hist_t_05-05.csv")
    forecast_path = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\data\s3_downloaded_datasets\temperature_forecast_data.csv"

    date_min = datetime(2025, 4, 5, 0, 0)
    date_max = datetime(2025, 5, 5, 23, 45)

    merge_regional_temperature_data(hist_folder, merged_hist_path)
