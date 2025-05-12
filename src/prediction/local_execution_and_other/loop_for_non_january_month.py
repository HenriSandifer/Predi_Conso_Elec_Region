for day in range(start_day, num_days + 1):
        date_str = datetime(target_year, month_number, day). strftime("%Y-%m-%d")
        print(f"📅 Running  day: {date_str}")
        run_all_for_day(func_region, date_str)