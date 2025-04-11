from prediction.run_day import run_all_for_day
import calendar
from datetime import datetime
import argparse


def run_all_for_month(func_region, target_month, target_year):
    
    # Convert month name to number
    try:
        month_number = list(calendar.month_name).index(target_month)
    except ValueError:
        print(f"❌ Invalid month name: {target_month}")
        return
    
    if month_number == 0:
        print(f"❌ Please provide a full month name (e.g., 'March').")
        return
    
    #Get number of days in the month
    num_days = calendar.monthrange(target_year, month_number)[1]

    print(f"🚀 Running predictions for {func_region} for {target_month} {target_year}")

    # Loop through each day
    for day in range(1, num_days + 1):
        date_str = datetime(target_year, month_number, day). strftime("%Y-%m-%d")
        print(f"📅 Running  day: {date_str}")
        run_all_for_day(func_region, date_str)

    print(f"🏁 Finished predictions for {target_month} {target_year} in {func_region}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run all predictions for a given region and a given month.")
    parser.add_argument("--region", type=str, required=True, help="Region name (e.g., 'Auvergne-Rhône-Alpes')")
    parser.add_argument("--month", type=str, required=True, help="Target month (e.g., 'March')")
    parser.add_argument("--year", type=int, required=True, help="Year (e.g., 2025")

    args = parser.parse_args()
    run_all_for_month(args.region, args.month, args.year)