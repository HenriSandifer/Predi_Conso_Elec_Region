from datetime import datetime, timedelta, timezone
from src.evaluation.run_full_day_pred_eval import run_full_day_prediction_evaluation
from src.metrics_aggregation.func_aggregate_monthly_metrics import aggregate_monthly_metrics
from src.metrics_aggregation.func_aggregate_national_metrics import aggregate_national_metrics
from src.utils.dictionaries import region_abbr_caps_dict, region_abbr_dict


def run_evaluation(region, chosen_day_ymd):
    try:
        print(f" 🔬 Running evaluation for region {region} on {chosen_day_ymd} ...")
        run_full_day_prediction_evaluation(region, chosen_day_ymd)
        print("✅ Evaluation successful.")
        return
    except Exception as e:
        print(f"⚠️ Error during evaluation: {e}")
    
def infer_day():
    return (datetime.now(timezone.utc) + timedelta(days=-1, hours=2)).strftime("%Y-%m-%d")

def infer_regions():
    return list(region_abbr_caps_dict.keys())

def infer_month():
    return (datetime.now(timezone.utc) + timedelta(hours=2)).strftime("%Y-%m")

def run_monthly_aggregation(region, region_abbr_caps, chosen_month_ym, region_abbr_lwrc):
    try:
        print(f"📅 Running monthly aggregation job for region {region} for month  {chosen_month_ym}...")
        aggregate_monthly_metrics(region_abbr_caps, chosen_month_ym, region_abbr_lwrc)
        print("✅ Monthly aggregation successful.")
        return
    except Exception as e:
        print(f"⚠️ Error during aggregation: {e}")

def run_national_aggregation(chosen_month_ym):
    try:
        print(f"🇫🇷 Running national aggregation job for month {chosen_month_ym}...")
        aggregate_national_metrics(chosen_month_ym)
        print("✅ National aggregation successful.")
        return
    except Exception as e:
        print(f"⚠️ Error during aggregation: {e}")


if __name__ == "__main__":
    regions = infer_regions()
    chosen_day_ymd = infer_day()
    chosen_month_ym = infer_month()
    
    print("⚙️ Starting evaluation job...")
    for region in regions:
        run_evaluation(region, chosen_day_ymd)

    print("⚙️ Starting monthly metrics aggregation job...")
    for region in regions:
        region_abbr_caps = region_abbr_caps_dict[region]
        region_abbr_lwrc = region_abbr_dict[region]
        run_monthly_aggregation(region, region_abbr_caps, chosen_month_ym, region_abbr_lwrc)

    print("⚙️ Starting national metrics aggregation job...")
    run_national_aggregation(chosen_month_ym)