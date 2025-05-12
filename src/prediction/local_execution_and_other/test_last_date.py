from utils_s3 import get_last_fully_predicted_date

# Region-to-abbreviation map
region_abbr_caps_dict = {
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
}

# ✅ Change these to test other regions/months
region_name = "Bourgogne-Franche-Comté"
target_month = "2025-01"

region_abbr = region_abbr_caps_dict.get(region_name)

if region_abbr is None:
    print(f"❌ Unknown region name: {region_name}")
else:
    print(f"🔍 Checking last fully predicted date for: {region_name} ({region_abbr}) - {target_month}")
    last_date = get_last_fully_predicted_date(region_abbr, target_month)
    print(f"📅 Last complete prediction day: {last_date if last_date else 'None found'}")
