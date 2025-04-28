import argparse
from func_aggregate_national_metrics import aggregate_national_metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--month", required=True, help="eg. 2025-04")
    args = parser.parse_args()

    aggregate_national_metrics(target_month=args.month)
