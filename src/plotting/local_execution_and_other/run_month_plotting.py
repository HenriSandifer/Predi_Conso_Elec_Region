from run_plot_eval import run_plot_eval
import calendar
from datetime import datetime
import argparse

def run_all_plot_for_month(region, target_month, target_year):
    
    month_number = target_month
    if not 1 <= month_number <= 12:
        print(f"❌ Invalid month number: {month_number}. Must be 1–12.")
        return

    target_month_ym = f"{target_year}-{month_number:02d}"
    
    #Get number of days in the month
    num_days = calendar.monthrange(target_year, month_number)[1]

    print(f"🚀 Running plots for {region} for {target_month_ym}")

    # Loop through each day
    start_day = 6

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
    }.get(region)

    if not region_abbr_caps:
        print(f"❌ Unknown region: {region}")
        return
    
    for day in range(start_day, num_days + 1):
        date_ymd = datetime(target_year, month_number, day). strftime("%Y-%m-%d")
        print(f"📅 Running  day: {date_ymd}")
        run_plot_eval(region, date_ymd)

    print(f"🏁 Finished plots for {target_month} {target_year} in {region}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run all predictions for a given region and a given month.")
    parser.add_argument("--region", type=str, required=True, help="Region name (e.g., 'Auvergne-Rhône-Alpes')")
    parser.add_argument("--month", type=int, required=True, help="Target month number (e.g., 1 for January)")
    parser.add_argument("--year", type=int, required=True, help="Year (e.g., 2025")

    args = parser.parse_args()
    run_all_plot_for_month(args.region, args.month, args.year)