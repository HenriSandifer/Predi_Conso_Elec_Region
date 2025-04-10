# Plot full-day only
    plt.figure(figsize=(12, 5))
    plt.plot(df_eval_full["Datetime"], df_eval_full["y_real"], label="Real", linewidth=2)
    plt.plot(df_eval_full["Datetime"], df_eval_full["y_pred"], label="Predicted", linestyle="--")
    plt.title(f"{region_abbr_caps} - {chosen_day} - {run_time_str} D0 Run\nPredicted vs Real Consumption")
    plt.xlabel("Time")
    plt.ylabel("MW")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(run_time_folder, f"prediction_plot_{region_abbr_lwrc}_{run_time_str}.png")
    plt.savefig(plot_path)
    print(f"📈 Plot saved to: {plot_path}")