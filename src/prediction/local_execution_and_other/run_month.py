from run_day import run_all_for_day
import calendar
from datetime import datetime, timedelta
import argparse
from utils_s3 import get_last_fully_predicted_date

def run_all_for_month(func_region, target_month, target_year):
    
    month_number = target_month
    if not 1 <= month_number <= 12:
        print(f"❌ Invalid month number: {month_number}. Must be 1–12.")
        return

    target_month_ym = f"{target_year}-{month_number:02d}"
    
    #Get number of days in the month
    num_days = calendar.monthrange(target_year, month_number)[1]

    print(f"🚀 Running predictions for {func_region} for {target_month_ym}")

    # Loop through each day
    start_day = 1

    region_abbr_caps = {
        "Nouvelle-Aquitaine": "NAQ",
        "Occitanie": "OCC",
        "Île-de-France": "IDF",
        "Auvergne-Rhône-Alpes": "ARA",
        "Grand Est": "GRE",
        "Bretagne": "BRE",
        "Provence-Alpes-Côte d'Azur": "PAC",
        "Hauts-de-France": "HDF",
        "Pays de la Loire": "PAL",
        "Centre-Val de Loire": "CVL",
        "Bourgogne-Franche-Comté": "BFC"
    }.get(func_region)

    if not region_abbr_caps:
        print(f"❌ Unknown region: {func_region}")
        return
    
    print(f"🔍 Checking last fully predicted date for: {func_region} ({region_abbr_caps}) - {target_month}")
    last_pred_date = get_last_fully_predicted_date(region_abbr_caps, target_month_ym)
    print(f"last_pred_date is : {last_pred_date}")

    if last_pred_date:
        next_date = last_pred_date + timedelta(days=1)
        start_day = next_date.day
        print(f"📌 Resuming from {next_date} (last complete = {last_pred_date})")
    else:
        # No predictions yet — start from start_day
        start_day = 1
        print(f"📌 No predictions found for month {target_month_ym}. Starting from day one.")

    for day in range(start_day, num_days + 1):
        date_str = datetime(target_year, month_number, day). strftime("%Y-%m-%d")
        print(f"📅 Running  day: {date_str}")
        run_all_for_day(func_region, date_str)

    print(f"🏁 Finished predictions for {target_month} {target_year} in {func_region}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run all predictions for a given region and a given month.")
    parser.add_argument("--region", type=str, required=True, help="Region name (e.g., 'Auvergne-Rhône-Alpes')")
    parser.add_argument("--month", type=int, required=True, help="Target month number (e.g., 1 for January)")
    parser.add_argument("--year", type=int, required=True, help="Year (e.g., 2025")

    args = parser.parse_args()
    run_all_for_month(args.region, args.month, args.year)