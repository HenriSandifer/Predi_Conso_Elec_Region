"""Adapt according to decision of overwriting or not
and to include data from the latest API pull, not from CSVs """

# Load the files
df_1 = pd.read_csv("cons_04-08.csv", parse_dates=["Datetime"])
df_2 = pd.read_csv("cons_04-05.csv", parse_dates=["Datetime"])
df_base = pd.read_csv("reg_2025_cons.csv", parse_dates=["Datetime"])

# === STEP 1: Merge df_2 and df_1 ===
cutoff_1 = df_1["Datetime"].min()
df_2_trimmed = df_2[df_2["Datetime"] < cutoff_1]
merged_1_2 = pd.concat([df_2_trimmed, df_1], ignore_index=True).sort_values("Datetime")

# === STEP 2: Merge df_base and the result above ===
cutoff_2 = merged_1_2["Datetime"].min()
df_base_trimmed = df_base[df_base["Datetime"] < cutoff_2]
final_merged = pd.concat([df_base_trimmed, merged_1_2], ignore_index=True).sort_values("Datetime")

# (Optional) Save the final clean file
final_merged.to_csv("reg_2025_cons_updated.csv", index=False)

# Other concat command
df_combined = pd.concat(all_new_cons_data).sort_values("Datetime")