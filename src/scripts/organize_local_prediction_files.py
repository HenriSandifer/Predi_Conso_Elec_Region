import os
import shutil

def organize_prediction_files(base_path):
    """
    Creates a "pred" folder inside each runtime folder, and transfers the
    pred files present inside the runtime folder into the newly created
    "pred" folder

    """

    months = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05"]

    for region in os.listdir(base_path):
        print(f"region is :{region}")
        region_path = os.path.join(base_path, region)
        if not os.path.isdir(region_path):
            continue

        for month in months:
            print(f"month is : {month}")
            month_path = os.path.join(region_path, month)
            if not os.path.isdir(month_path):
                continue

            for day_folder in os.listdir(month_path):
                day_path = os.path.join(month_path, day_folder)
                if not os.path.isdir(day_path):
                    continue

                for run_time_folder in os.listdir(day_path):
                    run_path = os.path.join(day_path, run_time_folder)
                    if not os.path.isdir(run_path):
                        continue

                    pred_folder = os.path.join(run_path, "pred")
                    os.makedirs(pred_folder, exist_ok=True)

                    for file in os.listdir(run_path):
                        if file.startswith("pred") and file.endswith(".csv"):
                            src = os.path.join(run_path, file)
                            dst = os.path.join(pred_folder, file)
                            try:
                                shutil.move(src, dst)
                                print(f"✅ Moved: {file} → {pred_folder}")
                            except Exception as e:
                                print(f"❌ Failed to move {file}: {e}")

if __name__ == "__main__":
    base_path = r"C:\Users\Henri\Documents\GitHub\Predi_Conso_Elec_Region\Predictions_archive"
    organize_prediction_files(base_path)
