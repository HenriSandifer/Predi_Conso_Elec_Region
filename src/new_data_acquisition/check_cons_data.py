from utils_s3 import read_csv_from_s3
import pandas as pd

df_cons = read_csv_from_s3("raw_data/real_cons_data.csv")

print(df_cons.columns)
print(df_cons["Datetime"].min(), "→", df_cons["Datetime"].max())

df_cons["Datetime"] = pd.to_datetime(df_cons["Datetime"])

print(df_cons.tail(30))
