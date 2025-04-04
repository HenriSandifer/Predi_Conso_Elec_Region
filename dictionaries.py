model_delta = {
        "M48": 48,
        "M36": 36,
        "M24": 24,
        "M18": 18,
        "M12": 12
    }

region_abbr_caps_dict = {
        "Nouvelle-Aquitaine": "NAQ",
        "Occitanie": "OCC",
        "Île-de-France": "IDF",
        "Auvergne-Rhône-Alpes": "ARA",
        "Grand Est": "GRE",
        "Normandie": "NOR",
        "Bretagne": "BRE",
        "Provence-Alpes-Côte d'Azur": "PAC",
        "Hauts-de-France": "HDF",
        "Pays de la Loire": "PAL",
        "Centre-Val de Loire": "CVL",
        "Bourgogne-Franche-Comté": "BFC"
    }

region_abbr_dict = {
        "Nouvelle-Aquitaine": "naq",
        "Occitanie": "occ",
        "Île-de-France": "idf",
        "Auvergne-Rhône-Alpes": "ara",
        "Grand Est": "gre",
        "Normandie": "nor",
        "Bretagne": "bre",
        "Provence-Alpes-Côte d'Azur": "pac",
        "Hauts-de-France": "hdf",
        "Pays de la Loire": "pal",
        "Centre-Val de Loire": "cvl",
        "Bourgogne-Franche-Comté": "bfc"
    }

run_time_dict = {
        "02:00:00": 2,
        "08:00:00": 8,
        "14:00:00": 14,
        "20:00:00": 20
    }

holiday_zones = {
    "Auvergne-Rhône-Alpes": "A",
    "Bourgogne-Franche-Comté": "A",
    "Bretagne": "B",
    "Centre-Val de Loire": "B",
    "Grand Est": "B",
    "Hauts-de-France": "B",
    "Île-de-France": "C",
    "Normandie": "B",
    "Nouvelle-Aquitaine": "A",
    "Occitanie": "C",
    "Pays de la Loire": "B",
    "Provence-Alpes-Côte d'Azur": "B"  # Straight apostrophe
}

lag_roll_features_by_model = {
    "M48": ["lag_48h", "rolling_24h", "rolling_72h"],
    "M36": ["lag_36h", "rolling_24h", "rolling_72h"],
    "M24": ["lag_24h", "rolling_24h", "rolling_48h"],
    "M18": ["lag_18h", "lag_24h", "rolling_24h", "rolling_72h"],
    "M12": ["lag_12h", "lag_24h", "rolling_12h", "rolling_24h"]
}

lag_feature_multipliers_by_model = {
    "M12": {
        "lag_12h": 12,
        "lag_24h": 24,
    },
    "M18": {
        "lag_18h": 18,
        "lag_24h": 24,
    },
    "M24": {
        "lag_24h": 24,
    },
    "M36": {
        "lag_36h": 36,
    },
    "M48": {
        "lag_48h": 48,
    }
}


roll_feature_multipliers = {
    "rolling_12h": 48, 
    "rolling_24h": 96,
    "rolling_48h": 192,
    "rolling_72h": 288
}

prediction_timeframes = {
        ("M48", "02:00:00"): {"start": "12:00:00", "end": "23:45:00"},
        ("M48", "08:00:00"): {"start": "18:00:00", "end": "23:45:00"},

        ("M36", "02:00:00"): {"start": "00:00:00", "end": "11:45:00"},
        ("M36", "08:00:00"): {"start": "06:00:00", "end": "17:45:00"},
        ("M36", "14:00:00"): {"start": "12:00:00", "end": "23:45:00"},
        ("M36", "20:00:00"): {"start": "18:00:00", "end": "23:45:00"},

        ("M24", "08:00:00"): {"start": "00:00:00", "end": "05:45:00"},
        ("M24", "14:00:00"): {"start": "06:00:00", "end": "11:45:00"},
        ("M24", "20:00:00"): {"start": "12:00:00", "end": "17:45:00"},

        ("M18", "14:00:00"): {"start": "00:00:00", "end": "05:45:00"},
        ("M18", "20:00:00"): {"start": "06:00:00", "end": "11:45:00"},

        ("M12", "20:00:00"): {"start": "00:00:00", "end": "05:45:00"} 
}

from collections import defaultdict

models_by_run_time = defaultdict(list)
for (model, run_time), _ in prediction_timeframes.items():
    models_by_run_time[run_time].append(model)

weather_stations = {
    "Hauts-de-France": [
        {"ID": "07005", "Nom": "ABBEVILLE"},
        {"ID": "07015", "Nom": "LILLE-LESQUIN"}
    ],
    "Normandie": [
        {"ID": "07020", "Nom": "PTE DE LA HAGUE"},
        {"ID": "07027", "Nom": "CAEN-CARPIQUET"},
        {"ID": "07037", "Nom": "ROUEN-BOOS"},
        {"ID": "07139", "Nom": "ALENCON"}
    ],
    "Bretagne": [
        {"ID": "07110", "Nom": "BREST-GUIPAVAS"},
        {"ID": "07117", "Nom": "PLOUMANAC'H"},
        {"ID": "07130", "Nom": "RENNES-ST JACQUES"},
        {"ID": "07207", "Nom": "BELLE ILE-LE TALUT"}
    ],
    "Île-de-France": [
        {"ID": "07149", "Nom": "ORLY"}
    ],
    "Grand Est": [
        {"ID": "07072", "Nom": "REIMS-PRUNAY"},
        {"ID": "07168", "Nom": "TROYES-BARBEREY"},
        {"ID": "07181", "Nom": "NANCY-OCHEY"},
        {"ID": "07190", "Nom": "STRASBOURG-ENTZHEIM"}
    ],
    "Pays de la Loire": [
        {"ID": "07222", "Nom": "NANTES-BOUGUENAIS"}
    ],
    "Centre-Val de Loire": [
        {"ID": "07240", "Nom": "TOURS"},
        {"ID": "07255", "Nom": "BOURGES"}
    ],
    "Bourgogne-Franche-Comté": [
        {"ID": "07280", "Nom": "DIJON-LONGVIC"}
    ],
    "Nouvelle-Aquitaine": [
        {"ID": "07335", "Nom": "POITIERS-BIARD"},
        {"ID": "07434", "Nom": "LIMOGES-BELLEGARDE"},
        {"ID": "07510", "Nom": "BORDEAUX-MERIGNAC"},
        {"ID": "07607", "Nom": "MONT-DE-MARSAN"}
    ],
    "Auvergne-Rhône-Alpes": [
        {"ID": "07460", "Nom": "CLERMONT-FD"},
        {"ID": "07471", "Nom": "LE PUY-LOUDES"},
        {"ID": "07481", "Nom": "LYON-ST EXUPERY"},
        {"ID": "07577", "Nom": "MONTELIMAR"}
    ],
    "Provence-Alpes-Côte d'Azur": [
        {"ID": "07591", "Nom": "EMBRUN"},
        {"ID": "07650", "Nom": "MARIGNANE"},
        {"ID": "07661", "Nom": "CAP CEPET"},
        {"ID": "07690", "Nom": "NICE"}
    ],
    "Occitanie": [
        {"ID": "07621", "Nom": "TARBES-OSSUN"},
        {"ID": "07627", "Nom": "ST GIRONS"},
        {"ID": "07630", "Nom": "TOULOUSE-BLAGNAC"},
        {"ID": "07643", "Nom": "MONTPELLIER"}
    ]
}


