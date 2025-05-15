"""
THIS IS FOR A LOCAL RUN / NOT FOR AN S3 RUN
CHANGE FILE BEING IMPORTED FOR S3 RUN
-- in this case, import func_aggregate_monthly_metrics
-- instead of local_func_aggregate_monthly_metrics

"""

import argparse
from dictionaries import region_abbr_dict, region_abbr_caps_dict
from local_func_aggregate_monthly_metrics import aggregate_monthly_metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", required=True)
    parser.add_argument("--month", required=True, help="eg. 2025-04")
    args = parser.parse_args()

    region_abbr_caps = region_abbr_caps_dict[args.region]
    region_abbr_lwrc = region_abbr_dict[args.region]

    aggregate_monthly_metrics(region_abbr_caps, args.month, region_abbr_lwrc)
