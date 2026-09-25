import pandas as pd

RAW_AIRPORTS_PATH = "data/raw/airports.csv"
OUTPUT_PATH = "data/airports.csv"
MARKET_ASSUMPTIONS_PATH = "data/market_assumptions.csv"

#Read raw airports file
airports = pd.read_csv(RAW_AIRPORTS_PATH)

market_assumptions = pd.read_csv(
    MARKET_ASSUMPTIONS_PATH
)

AIRPORT_CODES = [
    "BRU",
    *market_assumptions["destination"].tolist(),
]

# Filtering selected airports
selected_airports = airports[
    airports["iata_code"].isin(AIRPORT_CODES)
].copy()

selected_airports = selected_airports[
    [
        "iata_code",
        "ident",
        "name",
        "municipality",
        "iso_country",
        "latitude_deg",
        "longitude_deg",
    ]
]

selected_airports = selected_airports.rename(
    columns={
        "iata_code": "iata",
        "ident": "icao",
        "municipality": "city",
        "iso_country": "country_code",
        "latitude_deg": "latitude",
        "longitude_deg": "longitude",
    }
)


selected_airports["iata"] = pd.Categorical(
    selected_airports["iata"],
    categories=AIRPORT_CODES,
    ordered=True,
)

selected_airports = selected_airports.sort_values("iata")


# Safety check
found_codes = set(selected_airports["iata"].astype(str))
expected_codes = set(AIRPORT_CODES)

missing_codes = expected_codes - found_codes

if missing_codes:
    raise ValueError(
        f"Missing airports in source dataset: {sorted(missing_codes)}"
    )

selected_airports.to_csv(
    OUTPUT_PATH,
    index=False,
)

print(f"Created {OUTPUT_PATH}")
print(selected_airports.to_string(index=False))

