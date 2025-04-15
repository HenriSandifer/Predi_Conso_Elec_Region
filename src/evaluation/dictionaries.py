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


weather_coordinates = {
    "Auvergne-Rhône-Alpes": [
        {"city": "Lyon", "latitude": 45.764043, "longitude": 4.835659},
        {"city": "Saint-Étienne", "latitude": 45.439695, "longitude": 4.387178},
        {"city": "Grenoble", "latitude": 45.188529, "longitude": 5.724524},
        {"city": "Clermont-Ferrand", "latitude": 45.777222, "longitude": 3.087025}
    ],
    "Bourgogne-Franche-Comté": [
        {"city": "Dijon", "latitude": 47.322047, "longitude": 5.04148},
        {"city": "Besançon", "latitude": 47.237829, "longitude": 6.024053},
        {"city": "Belfort", "latitude": 47.639674, "longitude": 6.863849},
        {"city": "Chalon-sur-Saône", "latitude": 46.782972, "longitude": 4.852051}
    ],
    "Brittany": [
        {"city": "Rennes", "latitude": 48.117266, "longitude": -1.677793},
        {"city": "Brest", "latitude": 48.390394, "longitude": -4.486076},
        {"city": "Quimper", "latitude": 47.996092, "longitude": -4.102201},
        {"city": "Lorient", "latitude": 47.748252, "longitude": -3.370244}
    ],
    "Centre-Val de Loire": [
        {"city": "Orléans", "latitude": 47.902964, "longitude": 1.909251},
        {"city": "Tours", "latitude": 47.394144, "longitude": 0.68484},
        {"city": "Bourges", "latitude": 47.081012, "longitude": 2.398782},
        {"city": "Chartres", "latitude": 48.443892, "longitude": 1.489013}
    ],
    "Corsica": [
        {"city": "Ajaccio", "latitude": 41.919229, "longitude": 8.738635},
        {"city": "Bastia", "latitude": 42.697283, "longitude": 9.450881},
        {"city": "Corte", "latitude": 42.306382, "longitude": 9.150099},
        {"city": "Porto-Vecchio", "latitude": 41.591368, "longitude": 9.279493}
    ],
    "Grand Est": [
        {"city": "Strasbourg", "latitude": 48.573405, "longitude": 7.752111},
        {"city": "Reims", "latitude": 49.258329, "longitude": 4.031696},
        {"city": "Metz", "latitude": 49.119308, "longitude": 6.175716},
        {"city": "Nancy", "latitude": 48.692054, "longitude": 6.184417}
    ],
    "Hauts-de-France": [
        {"city": "Lille", "latitude": 50.62925, "longitude": 3.057256},
        {"city": "Amiens", "latitude": 49.894067, "longitude": 2.295753},
        {"city": "Roubaix", "latitude": 50.69421, "longitude": 3.17456},
        {"city": "Dunkerque", "latitude": 51.034368, "longitude": 2.376776}
    ],
    "Île-de-France": [
        {"city": "Paris", "latitude": 48.856613, "longitude": 2.352222},
        {"city": "Boulogne-Billancourt", "latitude": 48.835537, "longitude": 2.241843},
        {"city": "Saint-Denis", "latitude": 48.936181, "longitude": 2.357443},
        {"city": "Argenteuil", "latitude": 48.947209, "longitude": 2.246684}
    ],
    "Normandy": [
        {"city": "Rouen", "latitude": 49.443232, "longitude": 1.099971},
        {"city": "Caen", "latitude": 49.182863, "longitude": -0.370679},
        {"city": "Le Havre", "latitude": 49.49437, "longitude": 0.107929},
        {"city": "Cherbourg", "latitude": 49.633731, "longitude": -1.622137}
    ],
    "Nouvelle-Aquitaine": [
        {"city": "Bordeaux", "latitude": 44.837789, "longitude": -0.57918},
        {"city": "Limoges", "latitude": 45.833619, "longitude": 1.261105},
        {"city": "Poitiers", "latitude": 46.580224, "longitude": 0.340375},
        {"city": "Pau", "latitude": 43.2951, "longitude": -0.370797}
    ],
    "Occitanie": [
        {"city": "Toulouse", "latitude": 43.604652, "longitude": 1.444209},
        {"city": "Montpellier", "latitude": 43.610769, "longitude": 3.876716},
        {"city": "Nîmes", "latitude": 43.836699, "longitude": 4.360054},
        {"city": "Perpignan", "latitude": 42.688659, "longitude": 2.894833}
    ],
    "Pays de la Loire": [
        {"city": "Nantes", "latitude": 47.218371, "longitude": -1.553621},
        {"city": "Angers", "latitude": 47.478419, "longitude": -0.563166},
        {"city": "Le Mans", "latitude": 48.00611, "longitude": 0.199556},
        {"city": "Saint-Nazaire", "latitude": 47.273498, "longitude": -2.213848}
    ],
    "Provence-Alpes-Côte d'Azur": [
        {"city": "Marseille", "latitude": 43.296482, "longitude": 5.36978},
        {"city": "Nice", "latitude": 43.710173, "longitude": 7.261953},
        {"city": "Toulon", "latitude": 43.124228, "longitude": 5.928},
        {"city": "Avignon", "latitude": 43.949317, "longitude": 4.805528}
]}
